from core.skill_manager import BaseSkill
from playwright.sync_api import sync_playwright
import os

class BrowserSkill(BaseSkill):
    """
    提供浏览器自动化功能：网页访问、内容提取、截图。
    模仿 OpenClaw 的浏览器能力。
    """
    
    def run(self, action="visit", url=None, selector=None):
        if not url and action != "close":
            return "请提供 URL"
            
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                if action == "visit":
                    page.goto(url)
                    # 简单提取标题和摘要
                    title = page.title()
                    text = page.inner_text("body")[:1000] # 获取前 1000 字符
                    return f"标题: {title}\n内容摘要: {text}"
                
                elif action == "screenshot":
                    page.goto(url)
                    shot_path = f"screenshot_{os.urandom(4).hex()}.png"
                    page.screenshot(path=shot_path)
                    return f"截图已保存至: {shot_path}"
                
                elif action == "extract":
                    page.goto(url)
                    if selector:
                        element = page.query_selector(selector)
                        return element.inner_text() if element else "未找到选择器"
                    return "请提供 CSS 选择器"
                
            except Exception as e:
                return f"浏览器操作失败: {str(e)}"
            finally:
                browser.close()
        
        return "不支持的浏览器动作"
