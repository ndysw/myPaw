import os
import importlib.util
import inspect

class SkillManager:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir
        self.skills = {}

    def load_skills(self):
        if not os.path.exists(self.skills_dir):
            return
        
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                skill_name = filename[:-3]
                file_path = os.path.join(self.skills_dir, filename)
                
                spec = importlib.util.spec_from_file_location(skill_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 寻找继承自 BaseSkill 的类 (假设我们定义了一个基类)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and name.endswith("Skill"):
                        self.skills[skill_name] = obj()
                        print(f"加载技能: {skill_name}")

    def execute_skill(self, skill_name, *args, **kwargs):
        if skill_name in self.skills:
            return self.skills[skill_name].run(*args, **kwargs)
        return f"技能 {skill_name} 未找到"

class BaseSkill:
    def run(self, *args, **kwargs):
        raise NotImplementedError("Skill must implement run method")
