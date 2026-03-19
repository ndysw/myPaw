import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QStatusBar,
    QListWidget,
    QSystemTrayIcon,
    QStyle,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QTextCursor
from core.llm_engine import LLMEngine
from core.skill_manager import SkillManager
from api.server import APIServer

# 定义立体拟物样式表 (QSS)
立体拟物_STYLESHEET = """
/* 主窗口 - 模拟真实桌面材质 */
QMainWindow {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2c3e50, stop:1 #1a2530);
}

/* 通用组件样式 */
QWidget {
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
    font-size: 14px;
}

/* 聊天显示区域 - 立体玻璃效果 */
QTextEdit {
    background-color: rgba(255, 255, 255, 0.05);
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 15px;
    font-size: 14px;
    line-height: 1.6;
}

/* 输入框 - 立体金属边框 */
QLineEdit {
    background-color: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 10px 12px;
    color: #ffffff;
}

/* 输入框聚焦状态 */
QLineEdit:focus {
    border-color: #4facfe;
}

/* 按钮 - 3D 立体金属效果 */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4facfe, stop:1 #00f2fe);
    color: white;
    border: 2px solid #2a7be4;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5ee7df, stop:1 #b490ca);
    border-color: #3a8bd8;
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a7be4, stop:1 #1a4b7a);
    border-color: #1a4b7a;
    padding: 8px 18px;
}

/* 列表控件 - 立体卡片效果 */
QListWidget {
    background-color: rgba(255, 255, 255, 0.05);
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    outline: none;
}

QListWidget::item {
    padding: 12px 15px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    margin: 4px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255,255,255,0.08);
}

QListWidget::item:hover {
    background: rgba(79, 172, 254, 0.15);
    border-color: rgba(79, 172, 254, 0.3);
}

QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(79, 172, 254, 0.3), stop:1 rgba(180, 144, 202, 0.3));
    border-color: rgba(79, 172, 254, 0.5);
}

/* 标签 - 立体发光效果 */
QLabel {
    font-weight: bold;
    color: #4facfe;
}

/* 状态栏 - 立体渐变 */
QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4facfe, stop:1 #00f2fe);
    color: white;
    border-top: 2px solid rgba(255,255,255,0.2);
    font-weight: bold;
}

/* 滚动条 - 立体金属质感 */
QScrollBar:vertical {
    background: rgba(255, 255, 255, 0.05);
    width: 16px;
    border-radius: 8px;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4facfe, stop:1 #00f2fe);
    min-height: 20px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.3);
}

QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5ee7df, stop:1 #b490ca);
}

/* 分割线 - 立体效果 */
QSplitter::handle {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255,255,255,0.2);
}

QSplitter::handle:hover {
    background: rgba(79, 172, 254, 0.2);
}
"""


class WorkerThread(QThread):
    finished_signal = pyqtSignal(str)

    def __init__(self, engine, prompt):
        super().__init__()
        self.engine = engine
        self.prompt = prompt

    def run(self):
        response = self.engine.chat(self.prompt)
        self.finished_signal.emit(response)


class MyPAWWindow(QMainWindow):
    # 定义跨线程同步信号: (发送者, 内容, 是否为用户)
    mobile_message_signal = pyqtSignal(str, str, bool)

    def __init__(self):
        super().__init__()

        # 连接信号到 UI 更新方法
        self.mobile_message_signal.connect(self.append_chat)

        # 初始化后端组件
        self.skill_manager = SkillManager()
        self.skill_manager.load_skills()

        self.engine = LLMEngine()
        self.engine.set_skill_manager(self.skill_manager)

        # 启动后端服务
        from api.server import set_llm_engine, set_on_message_callback

        self.api_server = APIServer()
        set_llm_engine(self.engine)
        set_on_message_callback(self.on_mobile_message) # 注入手机消息回调
        self.api_server.start()

        # 设置托盘图标
        self.initTray()

        # 初始化界面
        self.initUI()

        # 显示服务器地址
        server_url = self.api_server.get_server_url()
        print(f"[myPAW] API 服务器地址: {server_url}")
        print(f"[myPAW] 手机端连接地址: {server_url}")

    def initTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setToolTip("myPAW - 自主 AI 助手")
        self.tray_icon.show()

    def initUI(self):
        self.setWindowTitle("myPAW - 自主 AI 助手中控台")
        self.setGeometry(100, 100, 1000, 750)
        self.setStyleSheet(立体拟物_STYLESHEET)

        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # 左侧面板
        left_panel = QVBoxLayout()

        # 工作区配置
        workspace_group = self._create_workspace_group()
        left_panel.addWidget(workspace_group)

        left_panel.addWidget(QLabel("已加载技能模块"))
        self.skill_list = QListWidget()
        for skill_name in self.skill_manager.skills.keys():
            self.skill_list.addItem(f" 🛠️  {skill_name}")
        left_panel.addWidget(self.skill_list)
        left_panel.addStretch()

        # 右侧面板
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        # 字体大小控制面板
        font_control_layout = QHBoxLayout()
        font_control_layout.setSpacing(10)

        font_label = QLabel("字体大小:")
        font_label.setStyleSheet("font-weight: bold; color: #4facfe; font-size: 14px;")

        # 字体减小按钮 - 蓝色
        self.font_minus_btn = QPushButton("A-")
        self.font_minus_btn.setFixedSize(70, 45)
        self.font_minus_btn.setToolTip("减小字体")
        self.font_minus_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: 2px solid #1a5276;
                border-radius: 12px;
                font-weight: bold;
                font-size: 24px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3498db;
                border-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a5276;
                border-color: #0e3a52;
            }
        """)

        # 字体重置按钮 - 紫色
        self.font_normal_btn = QPushButton("A")
        self.font_normal_btn.setFixedSize(70, 45)
        self.font_normal_btn.setToolTip("标准字体")
        self.font_normal_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: 2px solid #6c3483;
                border-radius: 12px;
                font-weight: bold;
                font-size: 24px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #9b59b6;
                border-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #6c3483;
                border-color: #4a235a;
            }
        """)

        # 字体增大按钮 - 绿色
        self.font_plus_btn = QPushButton("A+")
        self.font_plus_btn.setFixedSize(70, 45)
        self.font_plus_btn.setToolTip("增大字体")
        self.font_plus_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 2px solid #1e8449;
                border-radius: 12px;
                font-weight: bold;
                font-size: 24px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
                border-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
                border-color: #145a32;
            }
        """)

        self.font_size_label = QLabel("当前：14px")
        self.font_size_label.setStyleSheet(
            "color: #ffffff; font-weight: bold; font-size: 13px;"
        )

        font_control_layout.addWidget(font_label)
        font_control_layout.addWidget(self.font_minus_btn)
        font_control_layout.addWidget(self.font_normal_btn)
        font_control_layout.addWidget(self.font_plus_btn)
        font_control_layout.addWidget(self.font_size_label)
        font_control_layout.addStretch()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setAcceptRichText(True)
        self.chat_display.setHtml("")

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("在此下达您的自主任务指令...")
        self.input_field.returnPressed.connect(self.handle_send)

        send_btn = QPushButton("执 行")
        send_btn.setMinimumHeight(35)
        send_btn.clicked.connect(self.handle_send)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_field, 5)
        input_layout.addWidget(send_btn, 1)

        right_panel.addLayout(font_control_layout)
        right_panel.addWidget(QLabel("自主思考与执行过程"))
        right_panel.addWidget(self.chat_display)
        right_panel.addLayout(input_layout)

        layout.addLayout(left_panel, 1)
        layout.addLayout(right_panel, 3)

        # 获取服务器地址
        server_url = self.api_server.get_server_url()
        self.statusBar().showMessage(
            f" 系统就绪 | API服务器: {server_url} | 已加载 {len(self.skill_manager.skills)} 个技能 | 工作区：{os.getcwd()}"
        )

        # 字体大小调整功能
        self.current_font_size = 14
        self.font_size_label.setText(f"当前：{self.current_font_size}px")

        # 连接字体大小调整按钮
        self.font_minus_btn.clicked.connect(self.decrease_font_size)
        self.font_normal_btn.clicked.connect(self.reset_font_size)
        self.font_plus_btn.clicked.connect(self.increase_font_size)

    def _create_workspace_group(self):
        """创建工作区配置组件"""
        from PyQt5.QtWidgets import (
            QGroupBox,
            QLineEdit,
            QPushButton,
            QHBoxLayout,
            QLabel,
            QFileDialog,
        )

        group = QGroupBox("📁 编程工作区")
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # 工作区路径显示
        self.workspace_label = QLabel(os.getcwd())
        self.workspace_label.setStyleSheet("color: #e0e0e0; font-size: 12px;")
        self.workspace_label.setWordWrap(True)

        # 浏览按钮
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.setFixedSize(60, 28)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: 2px solid #2c3e50;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3498db;
                border-color: #2980b9;
            }
        """)
        self.browse_btn.clicked.connect(self._browse_workspace)

        layout.addWidget(QLabel("路径:"))
        layout.addWidget(self.workspace_label, 1)
        layout.addWidget(self.browse_btn)

        group.setLayout(layout)
        return group

    def _browse_workspace(self):
        """浏览选择工作区目录"""
        from PyQt5.QtWidgets import QFileDialog

        directory = QFileDialog.getExistingDirectory(
            self, "选择编程工作区目录", os.getcwd()
        )

        if directory:
            self._set_workspace(directory)

    def _set_workspace(self, path):
        """设置工作区并更新技能"""
        self.workspace_label.setText(path)

        # 更新 code_skill 和 build_skill 的工作区
        if "code_skill" in self.skill_manager.skills:
            self.skill_manager.skills["code_skill"].set_workspace(path)
        if "build_skill" in self.skill_manager.skills:
            self.skill_manager.skills["build_skill"].set_workspace(path)

        self.statusBar().showMessage(f"工作区已更改：{path}")

    def append_chat(self, sender, message, is_user=False):
        formatted_message = message.replace("\n", "<br>")
        current_time = self.get_current_time()

        if is_user:
            # 用户消息 - 蓝色立体气泡 (右对齐)
            html = f"""
            <table width="100%" cellspacing="0" cellpadding="8" style="margin-bottom: 10px;">
                <tr>
                    <td align="right">
                        <table cellspacing="0" cellpadding="12" style="
                            background-color: #3498db;
                            border: 2px solid #2980b9;
                            border-bottom: 4px solid #1a5276;
                            border-radius: 15px;
                            color: #ffffff;
                            max-width: 70%;
                        ">
                            <tr><td>
                                <div style="font-size: 11px; color: #aed6f1; font-weight: bold; margin-bottom: 5px;">👤 我</div>
                                <div style="font-size: 14px; line-height: 1.5;">{formatted_message}</div>
                                <div style="font-size: 10px; color: rgba(255,255,255,0.6); margin-top: 8px; text-align: right;">{current_time}</div>
                            </td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            """
        else:
            # 机器人消息 - 紫罗兰立体气泡 (左对齐)
            html = f"""
            <table width="100%" cellspacing="0" cellpadding="8" style="margin-bottom: 10px;">
                <tr>
                    <td align="left">
                        <table cellspacing="0" cellpadding="12" style="
                            background-color: #9b59b6;
                            border: 2px solid #8e44ad;
                            border-bottom: 4px solid #6c3483;
                            border-radius: 15px;
                            color: #ffffff;
                            max-width: 70%;
                        ">
                            <tr><td>
                                <div style="font-size: 11px; color: #e8daef; font-weight: bold; margin-bottom: 5px;">🤖 myPAW</div>
                                <div style="font-size: 14px; line-height: 1.5;">{formatted_message}</div>
                                <div style="font-size: 10px; color: rgba(255,255,255,0.6); margin-top: 8px; text-align: right;">{current_time}</div>
                            </td></tr>
                        </table>
                    </td>
                </tr>
            </table>
            """

        self.chat_display.append(html)
        self.chat_display.moveCursor(QTextCursor.End)

    def get_current_time(self):
        from datetime import datetime

        return datetime.now().strftime("%H:%M")

    def handle_send(self):
        prompt = self.input_field.text().strip()
        if prompt:
            self.append_chat("我", prompt, is_user=True)
            self.input_field.clear()
            self.statusBar().showMessage("正在进行 ReAct 推理执行中...")

            self.worker = WorkerThread(self.engine, prompt)
            self.worker.finished_signal.connect(self.on_reply)
            self.worker.start()

    def on_reply(self, response):
        self.append_chat("myPAW", response)
        self.statusBar().showMessage("任务已处理完成")

        self.tray_icon.showMessage(
            "myPAW 任务完成",
            "您的自主任务已执行完毕，请查看结果。",
            QSystemTrayIcon.Information,
            3000,
        )

    def on_mobile_message(self, sender, content, is_user=True):
        """处理来自手机端的消息同步到 UI (使用信号槽确保线程安全)"""
        self.mobile_message_signal.emit(sender, content, is_user)

    def decrease_font_size(self):
        if self.current_font_size > 10:
            self.current_font_size -= 1
            self.update_font_size()

    def increase_font_size(self):
        if self.current_font_size < 24:
            self.current_font_size += 1
            self.update_font_size()

    def reset_font_size(self):
        self.current_font_size = 14
        self.update_font_size()

    def update_font_size(self):
        self.font_size_label.setText(f"当前：{self.current_font_size}px")
        self.statusBar().showMessage(f"字体大小已调整为 {self.current_font_size}px")


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = MyPAWWindow()
    window.show()
    sys.exit(app.exec_())
