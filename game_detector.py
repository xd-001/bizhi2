# -*- coding: utf-8 -*-
import psutil
import win32gui
import win32con
from typing import List, Optional

class GameDetector:
    def __init__(self):
        self.game_processes = []

    def update_game_list(self, processes: List[str]):
        self.game_processes = [p.lower() for p in processes]

    def is_game_running(self) -> bool:
        if not self.game_processes:
            return False
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() in self.game_processes:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def get_fullscreen_windows(self):
        fullscreen_windows = []
        def enum_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                monitor_info = win32gui.GetMonitorInfo(
                    win32gui.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
                )
                monitor_rect = monitor_info.get("Monitor", (0, 0, 1920, 1080))
                mon_width = monitor_rect[2] - monitor_rect[0]
                mon_height = monitor_rect[3] - monitor_rect[1]
                if width >= mon_width * 0.95 and height >= mon_height * 0.95:
                    class_name = win32gui.GetClassName(hwnd)
                    if class_name not in ["Progman", "Shell_TrayWnd", "WorkerW"]:
                        fullscreen_windows.append(hwnd)
            return True
        win32gui.EnumWindows(enum_callback, None)
        return fullscreen_windows

    def get_monitor_of_window(self, hwnd: int) -> Optional[tuple]:
        monitor = win32gui.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        monitor_info = win32gui.GetMonitorInfo(monitor)
        return monitor_info.get("Monitor")
