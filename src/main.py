import sys
import os
# 将当前文件所在目录加入 sys.path，以便绝对导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pystray
from PIL import Image
import threading
import keyboard
from wallpaper_manager import WallpaperManager
from config_manager import ConfigManager
from settings_window import open_settings
from gallery_window import open_gallery

class TrayApp:
    def __init__(self):
        self.config = ConfigManager()
        self.manager = WallpaperManager(self.config)
        self.manager.start_rotation()
        self.register_hotkey()
        self.icon = None
    
    def register_hotkey(self):
        mods = self.config.get("hotkey", "hotkey_modifiers")
        key = self.config.get("hotkey", "hotkey_key")
        hotkey = '+'.join(mods + [key])
        keyboard.add_hotkey(hotkey, self.manual_switch)
    
    def manual_switch(self):
        self.manager.switch_next_monitor()
    
    def toggle_guest_mode(self):
        current = self.config.get("general", "guest_mode")
        self.config.set("general", "guest_mode", not current)
    
    def toggle_auto_start(self):
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        exe_path = sys.argv[0]
        if self.config.get("general", "auto_start"):
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "AutoWallpaperChanger", 0, winreg.REG_SZ, exe_path)
        else:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                try:
                    winreg.DeleteValue(key, "AutoWallpaperChanger")
                except:
                    pass
    
    def like_current(self):
        last_monitor = self.manager.monitors[self.manager.current_monitor_index]
        self.manager.classify_current_wallpaper(last_monitor, 'like')
    
    def dislike_current(self):
        last_monitor = self.manager.monitors[self.manager.current_monitor_index]
        self.manager.classify_current_wallpaper(last_monitor, 'dislike')
    
    def show_help(self):
        import webbrowser
        webbrowser.open("https://github.com/your/repo/wiki")
    
    def quit_app(self):
        self.manager.stop()
        keyboard.unhook_all()
        self.icon.stop()
        sys.exit(0)
    
    def create_tray_menu(self):
        return pystray.Menu(
            pystray.MenuItem("立即切换", self.manual_switch),
            pystray.MenuItem("喜欢当前壁纸", self.like_current),
            pystray.MenuItem("不喜欢当前壁纸", self.dislike_current),
            pystray.MenuItem("开机启动", self.toggle_auto_start, checked=lambda item: self.config.get("general", "auto_start")),
            pystray.MenuItem("访客模式", self.toggle_guest_mode, checked=lambda item: self.config.get("general", "guest_mode")),
            pystray.MenuItem("图库浏览", lambda: threading.Thread(target=open_gallery, args=(self.config,), daemon=True).start()),
            pystray.MenuItem("设置", lambda: threading.Thread(target=open_settings, args=(self.config, self.manager), daemon=True).start()),
            pystray.MenuItem("使用说明", self.show_help),
            pystray.MenuItem("退出", self.quit_app)
        )
    
    def run(self):
        if os.path.exists("icon.ico"):
            image = Image.open("icon.ico")
        else:
            # 创建一个空白图标避免崩溃
            image = Image.new('RGB', (64, 64), color='gray')
        self.icon = pystray.Icon("wallpaper_changer", image, "壁纸自动更换", self.create_tray_menu())
        self.icon.run()

if __name__ == "__main__":
    app = TrayApp()
    app.run()
