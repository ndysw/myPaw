from core.skill_manager import BaseSkill
import os

class FileOpsSkill(BaseSkill):
    """一个简单的文件操作技能示例"""
    
    def run(self, action="list", path="."):
        if action == "list":
            try:
                files = os.listdir(path)
                return f"目录 {path} 下的文件: {', '.join(files)}"
            except Exception as e:
                return f"读取目录失败: {str(e)}"
        elif action == "read":
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read(500) # 只读前 500 字符
            except Exception as e:
                return f"读取文件失败: {str(e)}"
        return "不支持的动作"
