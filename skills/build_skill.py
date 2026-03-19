import os
import subprocess
import threading
from core.skill_manager import BaseSkill


class BuildSkill(BaseSkill):
    """编译和运行技能 - 支持多种语言的编译和命令执行"""
    
    def __init__(self):
        super().__init__()
        self.workspace = os.getcwd()
        self.last_output = ""
    
    def set_workspace(self, path):
        """设置工作区目录"""
        if os.path.isdir(path):
            self.workspace = path
            return f"工作区已设置为：{path}"
        return f"错误：目录不存在 - {path}"
    
    def get_workspace(self):
        """获取当前工作区"""
        return self.workspace
    
    def run(self, action, command=None, file_path=None, language=None, **kwargs):
        """
        执行编译或运行操作
        
        参数:
            action: 操作类型
                - 'compile': 编译代码
                - 'run': 运行程序/命令
                - 'build': 执行构建命令 (如 mvn, gradle, npm 等)
                - 'test': 执行测试
            command: 要执行的命令
            file_path: 文件路径 (相对于工作区)
            language: 编程语言 (python, java, cpp, nodejs 等)
        """
        try:
            if action == 'compile':
                return self._compile(file_path, language, **kwargs)
            elif action == 'run':
                return self._run_command(command, file_path, **kwargs)
            elif action == 'build':
                return self._build(command, **kwargs)
            elif action == 'test':
                return self._test(command, **kwargs)
            else:
                return f"未知操作：{action}"
        except Exception as e:
            return f"执行失败：{str(e)}"
    
    def _compile(self, file_path, language, **kwargs):
        """编译代码文件"""
        # 确定文件路径
        if os.path.isabs(file_path):
            abs_path = file_path
        else:
            abs_path = os.path.join(self.workspace, file_path)
        
        if not os.path.exists(abs_path):
            return f"错误：文件不存在 - {abs_path}"
        
        # 根据语言选择编译命令
        compile_commands = {
            'java': f'javac "{abs_path}"',
            'cpp': f'g++ -o "{abs_path}.exe" "{abs_path}"',
            'c': f'gcc -o "{abs_path}.exe" "{abs_path}"',
            'cs': f'csc "/out:{abs_path}.exe" "{abs_path}"',
            'go': f'go build -o "{abs_path}.exe" "{abs_path}"',
            'rust': f'rustc -o "{abs_path}.exe" "{abs_path}"',
        }
        
        cmd = compile_commands.get(language.lower())
        if not cmd:
            return f"不支持的语言：{language}\n支持的语言：{', '.join(compile_commands.keys())}"
        
        return self._execute_command(cmd, os.path.dirname(abs_path))
    
    def _run_command(self, command, file_path=None, **kwargs):
        """运行程序或命令"""
        if command:
            # 直接执行命令
            return self._execute_command(command, self.workspace)
        
        # 根据文件类型自动选择运行方式
        if file_path:
            if os.path.isabs(file_path):
                abs_path = file_path
            else:
                abs_path = os.path.join(self.workspace, file_path)
            
            if not os.path.exists(abs_path):
                return f"错误：文件不存在 - {abs_path}"
            
            ext = os.path.splitext(abs_path)[1].lower()
            run_commands = {
                '.py': f'python "{abs_path}"',
                '.js': f'node "{abs_path}"',
                '.java': f'java -cp "{os.path.dirname(abs_path)}" {os.path.basename(abs_path)[:-5]}',
                '.exe': f'"{abs_path}"',
                '.sh': f'bash "{abs_path}"',
                '.bat': f'cmd /c "{abs_path}"',
            }
            
            cmd = run_commands.get(ext)
            if cmd:
                return self._execute_command(cmd, os.path.dirname(abs_path))
            else:
                return f"不支持的文件类型：{ext}"
        
        return "错误：请指定命令或文件路径"
    
    def _build(self, command, **kwargs):
        """执行构建命令"""
        return self._execute_command(command, self.workspace)
    
    def _test(self, command, **kwargs):
        """执行测试命令"""
        if not command:
            # 尝试自动检测测试命令
            test_commands = [
                'pytest',
                'npm test',
                'mvn test',
                'gradle test',
                'go test',
                'cargo test',
            ]
            for cmd in test_commands:
                result = self._execute_command(cmd, self.workspace, timeout=30)
                if 'no tests' not in result.lower() and 'error' not in result.lower():
                    return result
            return "未找到合适的测试命令，请手动指定"
        
        return self._execute_command(command, self.workspace)
    
    def _execute_command(self, command, cwd, timeout=120):
        """执行 shell 命令"""
        self.last_output = ""
        
        try:
            # 使用 subprocess 执行命令
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                return f"⚠️ 命令执行超时 (>{timeout}秒)，已强制终止\n命令：{command}"
            
            output = ""
            if stdout:
                output += f"📤 输出:\n{stdout}\n"
            if stderr:
                output += f"⚠️ 错误:\n{stderr}\n"
            
            return_code = process.returncode
            output += f"\n{'✅' if return_code == 0 else '❌'} 退出码：{return_code}"
            
            self.last_output = output
            return output
            
        except Exception as e:
            return f"执行异常：{str(e)}\n命令：{command}"
    
    def get_last_output(self):
        """获取最后一次执行输出"""
        return self.last_output


class PythonBuildSkill(BuildSkill):
    """Python 项目专用构建技能"""
    
    def __init__(self):
        super().__init__()
    
    def run(self, action, **kwargs):
        """Python 项目特定操作"""
        if action == 'install':
            return self._install_deps()
        elif action == 'venv':
            return self._create_venv()
        elif action == 'lint':
            return self._lint()
        elif action == 'format':
            return self._format()
        else:
            return super().run(action, **kwargs)
    
    def _install_deps(self):
        """安装依赖"""
        req_file = os.path.join(self.workspace, 'requirements.txt')
        if os.path.exists(req_file):
            return self._execute_command(f'pip install -r "{req_file}"', self.workspace)
        return "未找到 requirements.txt"
    
    def _create_venv(self):
        """创建虚拟环境"""
        venv_path = os.path.join(self.workspace, 'venv')
        return self._execute_command(f'python -m venv "{venv_path}"', self.workspace)
    
    def _lint(self):
        """代码检查"""
        return self._execute_command('flake8 .', self.workspace)
    
    def _format(self):
        """代码格式化"""
        return self._execute_command('black .', self.workspace)
