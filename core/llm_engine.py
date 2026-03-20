import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "your_api_key_here")
        # 使用 LongCat API 开放平台的 OpenAI 格式端点
        self.api_base = os.getenv("LLM_API_BASE", "https://api.longcat.chat/openai")
        self.model = os.getenv("LLM_MODEL", "LongCat-Flash-Thinking-2601")
        self.skill_manager = None # 将在 main_desktop.py 中注入

    def set_skill_manager(self, manager):
        self.skill_manager = manager

    def chat(self, prompt):
        """
        支持自主执行的聊天逻辑 (模仿 OpenClaw 的 ReAct 思维方式)。
        """
        # 动态获取系统桌面路径，帮助 AI 准确定位
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop_path):
            # 兼容一些非标准配置
            desktop_path = os.path.join(os.path.expanduser("~"), "桌面")

        system_prompt = f"""
        你是一个名为 myPAW 的自主 AI 助手，具备编程和实时信息检索能力。
        当前系统信息:
        - 操作系统: {os.name}
        - 当前用户桌面路径: {desktop_path}
        - 当前工作目录: {os.getcwd()}

        当你需要执行任务时，请输出以下格式：
        Thought: 你的思考过程
        Action: 技能名称
        Args: {{"参数名": "参数值"}}

        【重要规则】:
        1. 当你收到了 Observation (观察结果) 后，你应该根据结果直接向用户提供最终结论，除非你需要执行第二个不同的步骤。
        2. 不要重复执行完全相同的 Action。如果你已经执行过一次，且结果已经返回，请直接告诉用户结果。
        3. 最终回复不要再带 Action 标记。

        当前可用技能列表:
        
        【实时信息检索】
        - browser_skill: 浏览器操作
          * action='visit' - 访问网页并提取文本 (url)
          * action='screenshot' - 网页截图 (url)
          * action='extract' - 提取特定元素文本 (url, selector)
          注：当需要查询实时新闻（如新浪新闻）时，请先 visit 对应的官网地址（https://news.sina.com.cn/）。

        【系统与文件操作技能】
        - file_ops: 系统文件操作 (非常重要：当用户要求打开、读取本地文件或图片时，必须使用此技能)
          * action='open' - 调用系统默认程序直接打开文件或图片 (path: 文件绝对路径或相对工作区的路径)
          * action='list' - 列出目录下的文件 (path: 目录路径)
          * action='read' - 读取文本文件内容 (path: 文件路径)
        - system_skill: 操作系统控制 (action='launch'|'volume'|'status'|'info')

        【编程相关技能】
        - code_skill: 代码操作 (action='read'|'write'|'modify'|'create'|'delete'|'list'|'search', file_path, content, old_text, new_text, pattern)
        - build_skill: 编译和运行 (action='compile'|'run'|'build'|'test', file_path, command, language)
        
        【其他技能】
        - file_ops: 文件系统操作 (action='list'|'read', path)
        - calendar_skill: 日历管理 (action='list'|'add'|'clear', title, date, time)
        - email_skill: 发送邮件 (to_email, subject, body)
        - system_skill: 系统控制 (action='launch'|'volume'|'status', target, value)

        如果你能直接回答用户的问题，或者已经完成了任务，请直接给出最终结论。
        """

        # 初始化消息历史，并将 system_prompt 放入
        messages = [{"role": "system", "content": system_prompt}]
        messages.append({"role": "user", "content": prompt})

        # 支持多步决策 (最多循环 10 次，防止无限循环)
        last_image_tag = ""
        for step in range(10):
            response_text = self._call_api(messages)
            
            # 记录助手的回复
            messages.append({"role": "assistant", "content": response_text})

            # 匹配 Action 模式
            action_match = re.search(r"Action: (\w+)\nArgs: (\{.*\})", response_text, re.DOTALL)
            
            if action_match and self.skill_manager:
                skill_name = action_match.group(1)
                try:
                    args_str = action_match.group(2)
                    args = json.loads(args_str)
                    
                    # 执行技能并获得结果
                    print(f"[myPAW] 正在执行技能: {skill_name}, 参数: {args}")
                    result = self.skill_manager.execute_skill(skill_name, **args)
                    
                    # 记录执行结果中是否含有图片标记，用于最后透传
                    image_regex = r"(\[IMAGE:.*?\])"
                    image_match = re.search(image_regex, str(result))
                    if image_match:
                        last_image_tag = image_match.group(1)
                    
                    # 将执行结果反馈给 LLM
                    messages.append({"role": "user", "content": f"Observation: {result}"})
                    continue # 继续循环，让 LLM 决定下一步
                except Exception as e:
                    error_msg = f"解析或执行技能失败: {str(e)}"
                    messages.append({"role": "user", "content": f"Observation: {error_msg}"})
                    continue
            else:
                # 如果没有匹配到 Action，说明是最终回答
                final_response = response_text
                # --- 恢复下午成功的补丁逻辑：强制追加图片标记 ---
                if last_image_tag and last_image_tag not in final_response:
                    final_response += f"\n{last_image_tag}"
                return final_response

        return "任务执行步骤过多，已强制终止。"

    def _call_api(self, messages):
        if self.api_key == "your_api_key_here":
            return "模拟回复：[Action: browser_skill\nArgs: {\"action\": \"visit\", \"url\": \"https://news.sina.com.cn/\"}]\n(请在 .env 中配置您的 LongCat API Key)"

        import time
        max_retries = 3
        retry_delay = 1
        current_model = self.model

        for attempt in range(max_retries + 1):
            try:
                url = f"{self.api_base}/v1/chat/completions"
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                payload = {
                    "model": current_model,
                    "messages": messages,
                    "temperature": 0.5,
                    "max_tokens": 2048,
                    "stream": False
                }

                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                elif response.status_code == 429:
                    if attempt < max_retries:
                        # 429 错误：服务端模型限流或过载
                        print(f"[LLMEngine] LongCat API 触发 429 限流 (尝试 {attempt + 1}/{max_retries})，等待 {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        # 如果是默认模型触发限流，尝试降级到 Lite 模型
                        if current_model == "LongCat-Flash-Thinking-2601":
                            current_model = "LongCat-Flash-Lite"
                            print(f"[LLMEngine] 降级至模型: {current_model}")
                        continue
                    else:
                        return f"LongCat API 错误: 429 - 服务端模型限流，已达到最大重试次数。详细信息: {response.text}"
                else:
                    return f"LongCat API 错误: {response.status_code} - {response.text}"
            except Exception as e:
                if attempt < max_retries:
                    print(f"[LLMEngine] LongCat API 调用异常 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                return f"LongCat API 调用异常: {str(e)}"
