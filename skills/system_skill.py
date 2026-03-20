import os
import subprocess
import psutil
from core.skill_manager import BaseSkill
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class SystemSkill(BaseSkill):
    """
    提供本地操作系统控制功能：启动程序、控制音量、查看状态、查询电脑配置。
    支持的 action: "launch", "volume", "status", "info" 或 "config"。
    """
    
    def __init__(self):
        # 初始化音量控制接口
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
        except Exception:
            self.volume_ctrl = None

    def run(self, action="launch", target=None, value=None):
        if action == "launch":
            if not target:
                return "请指定要启动的程序名或路径"
            try:
                # 尝试通过命令启动 (如 notepad, calc) 或路径
                subprocess.Popen(target, shell=True)
                return f"已成功尝试启动程序: {target}"
            except Exception as e:
                return f"启动程序失败: {str(e)}"

        elif action == "volume":
            if self.volume_ctrl is None:
                return "未检测到音频输出设备，无法控制音量"
            
            try:
                # value 预期为 0.0 到 1.0 之间的浮点数，或字符串 "up"/"down"/"mute"
                current_vol = self.volume_ctrl.GetMasterVolumeLevelScalar()
                if value == "up":
                    new_vol = min(1.0, current_vol + 0.1)
                elif value == "down":
                    new_vol = max(0.0, current_vol - 0.1)
                elif value == "mute":
                    self.volume_ctrl.SetMute(1, None)
                    return "系统已静音"
                elif value == "unmute":
                    self.volume_ctrl.SetMute(0, None)
                    return "系统已取消静音"
                else:
                    new_vol = float(value)
                
                self.volume_ctrl.SetMasterVolumeLevelScalar(new_vol, None)
                return f"系统音量已调整至: {int(new_vol * 100)}%"
            except Exception as e:
                return f"音量控制失败: {str(e)}"

        elif action == "status":
            # 获取基础系统信息
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            battery_str = f"{battery.percent}%" if battery else "未知 (台式机?)"
            return f"系统状态报告:\n- CPU 使用率: {cpu}%\n- 内存占用: {mem}%\n- 电池电量: {battery_str}"
            
        elif action in ["info", "config"]:
            import platform
            uname = platform.uname()
            os_info = f"{uname.system} {uname.release} ({uname.version})"
            cpu_info = platform.processor()
            total_mem = round(psutil.virtual_memory().total / (1024 ** 3), 2)
            return f"系统配置信息:\n- 操作系统: {os_info}\n- 处理器 (CPU): {cpu_info}\n- 总物理内存: {total_mem} GB"

        return "不支持的系统动作"
