from core.skill_manager import BaseSkill
import os
import subprocess
import platform

class FileOpsSkill(BaseSkill):
    """
    文件操作技能。
    支持查看文件列表(list)、读取文本内容(read)，以及使用系统默认程序打开文件或图片(open)。
    允许访问任意系统路径。
    """
    
    def __init__(self):
        super().__init__()
        self.workspace = os.getcwd()  # 默认工作区为当前目录

    def set_workspace(self, path):
        """设置工作区目录"""
        if os.path.isdir(path):
            self.workspace = path
            return f"工作区已设置为：{path}"
        return f"错误：目录不存在 - {path}"

    def get_workspace(self):
        return self.workspace

    def _is_safe_path(self, path):
        """检查路径是否在授权的工作区内"""
        # 如果路径是绝对路径，检查是否以工作区开头
        abs_path = os.path.abspath(path)
        abs_workspace = os.path.abspath(self.workspace)
        return abs_path.startswith(abs_workspace)

    def run(self, action="list", path="."):
        # 如果没有提供绝对路径，则基于当前工作区构建绝对路径
        if not os.path.isabs(path):
            target_path = os.path.abspath(os.path.join(self.workspace, path))
        else:
            target_path = os.path.abspath(path)

        if action == "list":
            try:
                files = os.listdir(target_path)
                return f"目录 {target_path} 下的文件: {', '.join(files)}"
            except Exception as e:
                return f"读取目录失败: {str(e)}"
                
        elif action == "read":
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read(2000)
                    if len(content) == 2000:
                        content += "\n...(由于长度限制，仅显示前 2000 个字符)"
                    return content
            except Exception as e:
                return f"读取文件失败 (可能不是文本文件): {str(e)}"
                
        elif action == "open":
            try:
                if not os.path.exists(target_path):
                    return f"错误：文件或目录不存在 - {target_path}"
                    
                if platform.system() == 'Windows':
                    os.startfile(target_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', target_path))
                else:  # linux variants
                    subprocess.call(('xdg-open', target_path))
                    
                # 如果是图片文件，在返回信息中追加 [IMAGE: 路径] 标记，供手机端识别
                ext = os.path.splitext(target_path)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                    # 将路径中的反斜杠统一替换为正斜杠，避免 URL 编码中的歧义问题
                    safe_target_path = target_path.replace("\\", "/")
                    return f"已成功请求系统打开：{target_path}\n[IMAGE: {safe_target_path}]"
                
                return f"已成功请求系统打开：{target_path}"
            except Exception as e:
                return f"打开文件失败: {str(e)}"

        return f"不支持的动作：{action}。支持的动作有: list, read, open"
