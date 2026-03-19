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

        system_prompt = """
        你是一个名为 myPAW 的自主 AI 助手，具备编程和实时信息检索能力。
        当你需要执行任务时，请输出以下格式：
        Thought: 你的思考过程
        Action: 技能名称
        Args: {"参数名": "参数值"}

        当前可用技能列表:
        
        【实时信息检索】
        - browser_skill: 浏览器操作
          * action='visit' - 访问网页并提取文本 (url)
          * action='screenshot' - 网页截图 (url)
          * action='extract' - 提取特定元素文本 (url, selector)
          注：当需要查询实时新闻（如新浪新闻）时，请先 visit 对应的官网地址（https://news.sina.com.cn/）。

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
        for step in range(10):
            response_text = self._call_api(messages)
            
            # 记录助手的回复
            messages.append({"role": "assistant", "content": response_text})

            # 匹配 Action 模式
            action_match = re.search(r"Action: (\w+)\nArgs: (\{.*\})", response_text)
            
            if action_match and self.skill_manager:
                skill_name = action_match.group(1)
                try:
                    args_str = action_match.group(2)
                    args = json.loads(args_str)
                    
                    # 执行技能并获得结果
                    print(f"[myPAW] 正在执行技能: {skill_name}, 参数: {args}")
                    result = self.skill_manager.execute_skill(skill_name, **args)
                    
                    # 将执行结果反馈给 LLM
                    messages.append({"role": "user", "content": f"Observation: {result}"})
                    continue # 继续循环，让 LLM 决定下一步
                except Exception as e:
                    error_msg = f"解析或执行技能失败: {str(e)}"
                    messages.append({"role": "user", "content": f"Observation: {error_msg}"})
                    continue
            else:
                # 如果没有匹配到 Action，说明是最终回答
                return response_text

        return "任务执行步骤过多，已强制终止。"

    def _call_api(self, messages):
        if self.api_key == "your_api_key_here":
            return "模拟回复：[Action: browser_skill\nArgs: {\"action\": \"visit\", \"url\": \"https://news.sina.com.cn/\"}]\n(请在 .env 中配置您的 LongCat API Key)"

        try:
            url = f"{self.api_base}/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.5,
                "max_tokens": 2048,
                "stream": False
            }

            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"LongCat API 错误: {response.status_code} - {response.text}"
        except Exception as e:
            return f"LongCat API 调用异常: {str(e)}"
