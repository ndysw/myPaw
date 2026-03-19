import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
from core.skill_manager import BaseSkill
from dotenv import load_dotenv

load_dotenv()

class EmailSkill(BaseSkill):
    """
    提供发送邮件的功能。
    OpenClaw 的基础办公技能之一。
    """
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.qq.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.email_user = os.getenv("EMAIL_USER", "")
        self.email_pass = os.getenv("EMAIL_PASS", "")

    def run(self, to_email, subject, body):
        if not self.email_user or not self.email_pass:
            return "错误：请在 .env 文件中配置 EMAIL_USER 和 EMAIL_PASS (授权码)"
        
        if not to_email:
            return "错误：未指定收件人邮箱"

        try:
            # 构建邮件内容
            message = MIMEText(body, 'plain', 'utf-8')
            message['From'] = self.email_user
            message['To'] = to_email
            message['Subject'] = Header(subject, 'utf-8')

            # 连接服务器并发邮件
            # 使用 SSL 协议
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.email_user, self.email_pass)
            server.sendmail(self.email_user, [to_email], message.as_string())
            server.quit()
            
            return f"邮件已成功发送至 {to_email}，主题为：{subject}"
        except Exception as e:
            return f"邮件发送失败: {str(e)}"
