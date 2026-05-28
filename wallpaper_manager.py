# -*- coding: utf-8 -*-
import os
import random
import pythoncom
import win32com.client
from constants import STYLE_MAP

class WallpaperManager:
    def __init__(self):
        self.com_initialized = False
        self.wallpaper_com = None
        self._init_com()
        self.monitors = []
        self.current_wallpapers = {}
        self.screen_pause_state = {}
        self.current_switch_index = 0

    def _init_com(self):
        try:
            pythoncom.CoInitialize()
            self.com_initialized = True
            self.wallpaper_com = win32com.client.Dispatch("{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}")
            self._refresh_monitors()
        except Exception as e:
            print(f"COM初始化失败: {e}")

    def _refresh_monitors(self):
        try:
            monitors = self.wallpaper_com.GetMonitorRECTs()
            monitor_ids = self.wallpaper_com.GetMonitorIDs()
            self.monitors = []
            for i, (rect, mid) in enumerate(zip(monitors, monitor_ids)):
                self.monitors.append({"id": mid, "index": i, "rect": rect})
                if mid not in self.screen_pause_state:
                    self.screen_pause_state[mid] = False
        except Exception as e:
            print(f"获取显示器失败: {e}")

    def get_monitor_count(self):
        return len(self.monitors)

    def set_wallpaper(self, monitor_id, image_path, style="fill"):
        try:
            if not os.path.exists(image_path):
                return False
            self.wallpaper_com.SetWallpaper(monitor_id, image_path)
            position = STYLE_MAP.get(style, 0)
            self.wallpaper_com.SetPosition(position)
            self.current_wallpapers[monitor_id] = image_path
            return True
        except Exception as e:
            print(f"设置壁纸失败: {e}")
            return False

    def get_next_monitor(self):
        if not self.monitors:
            return None
        monitor = self.monitors[self.current_switch_index]
        self.current_switch_index = (self.current_switch_index + 1) % len(self.monitors)
        return monitor

    def is_screen_paused(self, monitor_id):
        return self.screen_pause_state.get(monitor_id, False)

    def set_screen_pause(self, monitor_id, paused):
        self.screen_pause_state[monitor_id] = paused

    def cleanup(self):
        if self.com_initialized:
            pythoncom.CoUninitialize()


class ImageLoader:
    @staticmethod
    def get_images_from_folder(folder_path, recursive=True):
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        images = []
        if not os.path.exists(folder_path):
            return images
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in image_extensions:
                        images.append(os.path.join(root, file))
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in image_extensions:
                    images.append(file_path)
        return images

    @staticmethod
    def get_random_image(folder_path, recursive=True):
        images = ImageLoader.get_images_from_folder(folder_path, recursive)
        return random.choice(images) if images else None
