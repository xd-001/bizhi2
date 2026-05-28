import win32gui
import win32con
import ctypes
from ctypes import wintypes

class GameDetector:
    def __init__(self, config):
        self.config = config
    
    def is_fullscreen_on_monitor(self, monitor_id):
        """检测指定显示器是否有全屏窗口"""
        # 简化：检测所有全屏窗口并判断所属显示器（需扩展，此处仅实现全屏检测）
        def enum_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                screen_width = win32api.GetSystemMetrics(0)
                screen_height = win32api.GetSystemMetrics(1)
                # 简单判断窗口是否覆盖全屏
                if width >= screen_width and height >= screen_height:
                    # 获取进程名
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                    process_path = win32process.GetModuleFileNameEx(process_handle, 0)
                    process_name = os.path.basename(process_path).lower()
                    game_list = self.config.get("general", "game_processes")
                    if any(g in process_name for g in game_list):
                        extra.append(True)
                        return False
            return True
        
        import win32api, win32process, os
        result = []
        win32gui.EnumWindows(enum_callback, result)
        return len(result) > 0
