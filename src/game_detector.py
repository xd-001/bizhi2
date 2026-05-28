import win32gui
import win32api
import win32process
import win32con
import os
from config_manager import ConfigManager

class GameDetector:
    def __init__(self, config: ConfigManager):
        self.config = config

    def is_fullscreen_on_monitor(self, monitor_id):
        """检测任何显示器上是否有全屏游戏进程"""
        def enum_callback(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                screen_width = win32api.GetSystemMetrics(0)
                screen_height = win32api.GetSystemMetrics(1)
                if width >= screen_width and height >= screen_height:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                        process_path = win32process.GetModuleFileNameEx(process_handle, 0)
                        process_name = os.path.basename(process_path).lower()
                        game_list = self.config.get("general", "game_processes")
                        if any(g in process_name for g in game_list):
                            result.append(True)
                            return False
                    except:
                        pass
            return True

        result = []
        win32gui.EnumWindows(enum_callback, result)
        return len(result) > 0
