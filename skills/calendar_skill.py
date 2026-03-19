from core.skill_manager import BaseSkill
import json
import os
from datetime import datetime

class CalendarSkill(BaseSkill):
    """
    一个基于本地 JSON 的日历管理系统，模拟 Google/Outlook Calendar。
    OpenClaw 的基础能力之一。
    """
    
    def __init__(self, data_file="calendar.json"):
        self.data_file = data_file
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load_events(self):
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_events(self, events):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=4, ensure_ascii=False)

    def run(self, action="list", title=None, date=None, time=None):
        events = self._load_events()
        
        if action == "list":
            if not events:
                return "当前没有日程安排"
            # 简单按日期排序并返回
            output = "您的日程安排：\n"
            for event in sorted(events, key=lambda x: (x.get('date', ''), x.get('time', ''))):
                output += f"- [{event['date']} {event['time']}] {event['title']}\n"
            return output

        elif action == "add":
            if not title or not date:
                return "添加日程需要标题和日期 (YYYY-MM-DD)"
            new_event = {
                "title": title,
                "date": date,
                "time": time or "全天",
                "created_at": datetime.now().isoformat()
            }
            events.append(new_event)
            self._save_events(events)
            return f"已成功添加日程：{title} ({date})"

        elif action == "clear":
            self._save_events([])
            return "已清空所有日程"

        return "不支持的日历动作"
