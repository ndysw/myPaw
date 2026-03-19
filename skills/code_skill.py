import os
import re
from core.skill_manager import BaseSkill


class CodeSkill(BaseSkill):
    """代码操作技能 - 支持读取、写入、修改代码文件"""
    
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
        """获取当前工作区"""
        return self.workspace
    
    def run(self, action, file_path=None, content=None, old_text=None, new_text=None, **kwargs):
        """
        执行代码操作
        
        参数:
            action: 操作类型
                - 'read': 读取文件内容
                - 'write': 写入文件 (创建或覆盖)
                - 'modify': 修改文件内容 (替换指定文本)
                - 'create': 创建新文件
                - 'delete': 删除文件
                - 'list': 列出目录内容
                - 'search': 搜索文件内容
            file_path: 文件路径 (相对于工作区)
            content: 写入的内容
            old_text: 要被替换的文本 (modify 操作使用)
            new_text: 替换后的文本 (modify 操作使用)
        """
        # 确保文件路径在工作区内
        if file_path:
            # 如果是绝对路径，检查是否在工作区内
            if os.path.isabs(file_path):
                abs_path = file_path
                if not abs_path.startswith(self.workspace):
                    return f"错误：文件必须在工作区 {self.workspace} 内"
            else:
                abs_path = os.path.join(self.workspace, file_path)
        else:
            abs_path = self.workspace
        
        try:
            if action == 'read':
                return self._read_file(abs_path)
            elif action == 'write':
                return self._write_file(abs_path, content)
            elif action == 'modify':
                return self._modify_file(abs_path, old_text, new_text)
            elif action == 'create':
                return self._create_file(abs_path, content)
            elif action == 'delete':
                return self._delete_file(abs_path)
            elif action == 'list':
                return self._list_directory(abs_path)
            elif action == 'search':
                pattern = kwargs.get('pattern', '')
                return self._search_in_file(abs_path, pattern)
            else:
                return f"未知操作：{action}"
        except Exception as e:
            return f"操作失败：{str(e)}"
    
    def _read_file(self, path):
        """读取文件内容"""
        if not os.path.exists(path):
            return f"错误：文件不存在 - {path}"
        if os.path.isdir(path):
            return self._list_directory(path)
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 显示文件信息
        file_size = os.path.getsize(path)
        line_count = content.count('\n') + 1
        
        return f"""📄 文件：{path}
📊 大小：{file_size} 字节 | 行数：{line_count}
{'='*50}
{content}"""
    
    def _write_file(self, path, content):
        """写入文件内容"""
        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ 文件已写入：{path}\n写入内容：{len(content)} 字节"
    
    def _modify_file(self, path, old_text, new_text):
        """修改文件内容 - 替换指定文本"""
        if not os.path.exists(path):
            return f"错误：文件不存在 - {path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_text not in content:
            return f"错误：未找到要替换的文本\n请在文件中确认以下内容是否存在:\n{old_text[:200]}..."
        
        # 计算替换次数
        count = content.count(old_text)
        new_content = content.replace(old_text, new_text)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"✅ 文件已修改：{path}\n替换了 {count} 处内容"
    
    def _create_file(self, path, content):
        """创建新文件"""
        if os.path.exists(path):
            return f"错误：文件已存在 - {path}"
        
        return self._write_file(path, content)
    
    def _delete_file(self, path):
        """删除文件"""
        if not os.path.exists(path):
            return f"错误：文件不存在 - {path}"
        
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        
        return f"✅ 已删除：{path}"
    
    def _list_directory(self, path):
        """列出目录内容"""
        if not os.path.exists(path):
            return f"错误：目录不存在 - {path}"
        
        items = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    # 获取文件扩展名
                    ext = os.path.splitext(item)[1]
                    icon = self._get_file_icon(ext)
                    items.append(f"{icon} {item}")
        except PermissionError:
            return f"错误：无权限访问 - {path}"
        
        return f"📂 目录：{path}\n{'='*50}\n" + "\n".join(items)
    
    def _get_file_icon(self, ext):
        """根据文件扩展名返回图标"""
        icons = {
            '.py': '🐍',
            '.js': '📜',
            '.ts': '📘',
            '.java': '☕',
            '.cpp': '⚙️',
            '.c': '⚙️',
            '.h': '⚙️',
            '.cs': '🔷',
            '.go': '🔹',
            '.rs': '🦀',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.xml': '📋',
            '.md': '📝',
            '.txt': '📄',
            '.yaml': '📝',
            '.yml': '📝',
        }
        return icons.get(ext.lower(), '📄')
    
    def _search_in_file(self, path, pattern):
        """在文件中搜索内容"""
        if not os.path.exists(path):
            return f"错误：文件不存在 - {path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        results = []
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                results.append(f"第 {i} 行：{line.strip()}")
        
        if not results:
            return f"未找到匹配 '{pattern}' 的内容"
        
        return f"🔍 搜索 '{pattern}' 的结果:\n" + "\n".join(results[:20])  # 限制显示 20 条
