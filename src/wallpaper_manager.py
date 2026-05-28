import ctypes
from ctypes import wintypes
import comtypes.client
import random
import os
from pathlib import Path
import time
import threading
from PIL import Image
import win32gui
import win32con
from .game_detector import GameDetector
from .config_manager import ConfigManager
from .utils import move_file_to_folder, get_images_from_folder

# 使用 IDesktopWallpaper COM 接口支持多屏独立设置
CLSID_DesktopWallpaper = '{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}'
IID_IDesktopWallpaper = '{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}'

class WallpaperManager:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.running = True
        self.current_monitor_index = 0
        self.monitors = self._get_monitors()
        self.desktop_wallpaper = None
        self._init_com()
        self.game_detector = GameDetector(config)
        self.lock = threading.Lock()
    
    def _init_com(self):
        try:
            self.desktop_wallpaper = comtypes.client.CreateObject(
                CLSID_DesktopWallpaper, interface=IID_IDesktopWallpaper
            )
        except Exception as e:
            print(f"COM初始化失败，将使用单屏模式: {e}")
            self.desktop_wallpaper = None
    
    def _get_monitors(self):
        """获取所有显示器标识符"""
        monitors = []
        if self.desktop_wallpaper:
            try:
                count = self.desktop_wallpaper.GetMonitorDevicePathCount()
                for i in range(count):
                    path = self.desktop_wallpaper.GetMonitorDevicePathAt(i)
                    monitors.append(path)
            except:
                pass
        if not monitors:
            monitors = ["PRIMARY"]  # 降级方案
        return monitors
    
    def set_wallpaper_for_monitor(self, monitor_id, image_path):
        """为指定显示器设置壁纸"""
        if not os.path.exists(image_path):
            return False
        try:
            if self.desktop_wallpaper and monitor_id != "PRIMARY":
                self.desktop_wallpaper.SetWallpaper(monitor_id, image_path)
            else:
                # 兼容旧版Windows或单屏
                ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            return True
        except Exception as e:
            print(f"设置壁纸失败 {monitor_id}: {e}")
            return False
    
    def get_random_wallpaper(self):
        """从当前活动图库（普通或访客）随机选择图片"""
        if self.config.get("general", "guest_mode"):
            folder = self.config.get("general", "guest_folder")
        else:
            folder = os.path.join(self.config.get("general", "main_folder"), "默认")
        images = get_images_from_folder(folder)
        if not images:
            # 降级到主文件夹
            images = get_images_from_folder(self.config.get("general", "main_folder"))
        return random.choice(images) if images else None
    
    def classify_current_wallpaper(self, monitor_id, action):
        """将当前壁纸移动到喜欢/不喜欢文件夹，action: 'like' or 'dislike'"""
        # 获取当前壁纸路径（由于多屏需要知道是哪张，简化：记录每个屏幕最后设置的壁纸）
        # 此处为了简洁，实现全局最后壁纸记录
        if not hasattr(self, 'last_wallpapers'):
            self.last_wallpapers = {}
        current_path = self.last_wallpapers.get(monitor_id)
        if not current_path or not os.path.exists(current_path):
            return
        if action == 'like':
            target = os.path.join(self.config.get("general", "main_folder"), "喜欢")
        else:
            target = os.path.join(self.config.get("general", "main_folder"), "不喜欢")
        move_file_to_folder(current_path, target)
    
    def switch_next_monitor(self):
        """轮流切换下一个显示器的壁纸"""
        if not self.running:
            return
        with self.lock:
            monitor = self.monitors[self.current_monitor_index]
            # 检查该显示器是否被暂停
            paused = self.config.get("monitor_pause", monitor, False)
            if not paused and not self.game_detector.is_fullscreen_on_monitor(monitor):
                # 获取新壁纸
                new_wallpaper = self.get_random_wallpaper()
                if new_wallpaper:
                    self.set_wallpaper_for_monitor(monitor, new_wallpaper)
                    # 记录当前壁纸用于分类
                    if not hasattr(self, 'last_wallpapers'):
                        self.last_wallpapers = {}
                    self.last_wallpapers[monitor] = new_wallpaper
            # 移动到下一个显示器
            self.current_monitor_index = (self.current_monitor_index + 1) % len(self.monitors)
    
    def start_rotation(self):
        """启动轮流切换线程"""
        def rotate_loop():
            interval = self.config.get("general", "switch_interval")
            while self.running:
                time.sleep(interval)
                if self.running:
                    self.switch_next_monitor()
        self.thread = threading.Thread(target=rotate_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
