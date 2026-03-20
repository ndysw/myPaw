from flask import Flask, request, jsonify
import threading
import logging

app = Flask(__name__)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

chat_history = []
llm_engine = None
on_message_callback = None  # 新增：消息回调函数


def set_llm_engine(engine):
    global llm_engine
    llm_engine = engine


def set_on_message_callback(callback):
    """设置当收到新消息（手机端）时的回调函数"""
    global on_message_callback
    on_message_callback = callback


@app.route("/")
def read_root():
    return jsonify({"status": "myPAW Flask API Server is running"})


@app.route("/messages", methods=["GET"])
def get_messages():
    after = request.args.get("after", 0, type=int)
    if after > 0:
        filtered = [msg for msg in chat_history if msg.get("timestamp", 0) > after]
        return jsonify(filtered)
    return jsonify(chat_history)


@app.route("/send", methods=["POST"])
def send_message():
    global chat_history

    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400

    import time

    content = data.get("content", "")
    sender = data.get("sender", "User")
    timestamp = int(time.time() * 1000)
    
    message = {
        "sender": sender,
        "content": content,
        "timestamp": timestamp,
        "isSent": True,
    }
    chat_history.append(message)

    # 如果桌面端注册了回调，通知 UI 显示手机端发来的消息
    if on_message_callback:
        on_message_callback(sender, content, is_user=True)

    if llm_engine and content:
        try:
            response = llm_engine.chat(content)
            ai_message = {
                "sender": "myPAW",
                "content": response,
                "timestamp": timestamp + 1,
                "isSent": False,
            }
            chat_history.append(ai_message)
            
            # 通知 UI 显示 AI 的回复
            if on_message_callback:
                on_message_callback("myPAW", response, is_user=False)
                
            return jsonify({"status": "success", "message": response})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "received", "message": content})


class APIServer:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.thread = None
        self.server = None

    def start(self):
        from werkzeug.serving import make_server
        self.server = make_server(self.host, self.port, app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"[API Server] 启动服务器: http://{self.host}:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.thread.join()

    def get_server_url(self):
        """获取手机端可连接的局域网 URL"""
        import socket
        display_host = self.host
        if self.host == "0.0.0.0":
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                display_host = s.getsockname()[0]
                s.close()
            except Exception:
                display_host = "127.0.0.1"
        return f"http://{display_host}:{self.port}/"
