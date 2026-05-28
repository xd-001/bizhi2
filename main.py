# -*- coding: utf-8 -*-
import sys
import os
import json
import winreg
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from constants import APP_NAME, DEFAULT_CONFIG, REG_PATH, REG_KEY
from wallpaper_manager import WallpaperManager, ImageLoader
from tray_icon import TrayIcon
from settings_dialog import SettingsDialog
from browser_dialog import BrowserDialog
from game_detector import GameDetector
from file_classifier import FileClassifier
from hotkey_manager import HotkeyManager

class WallpaperChanger(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.wm = WallpaperManager()
        self.game_detector = GameDetector()
        self.hotkey_mgr = HotkeyManager()
        self.config = self.load_config()
        self.classifier = None
        self.timer = QTimer()
        self.is_running = True
        self.visit_mode = self.config.get("visit_mode", False)

        self.tray = TrayIcon()
        self.setup_signals()
        self.init_classifier()
        self.timer.timeout.connect(self.switch_next_wallpaper)
        self.update_timer_interval()
        self.register_hotkey()

        self.game_check_timer = QTimer()
        self.game_check_timer.timeout.connect(self.check_games)
        self.game_check_timer.start(2000)

        self.timer.start()
        self.tray.show()
        self.set_auto_start(self.config.get("auto_start", False))
        self.game_detector.update_game_list(self.config.get("game_processes", []))

    def init_classifier(self):
        folder = self.get_current_main_folder()
        if folder and os.path.exists(folder):
            self.classifier = FileClassifier(folder)

    def get_current_main_folder(self):
        return self.config.get("visit_folder", "") if self.visit_mode else self.config.get("main_folder", "")

    def load_config(self):
        path = os.path.expanduser(f"~/.{APP_NAME.lower()}_config.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    cfg = DEFAULT_CONFIG.copy()
                    cfg.update(saved)
                    return cfg
            except:
                pass
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        path = os.path.expanduser(f"~/.{APP_NAME.lower()}_config.json")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def update_timer_interval(self):
        self.timer.setInterval(self.config.get("interval", 30) * 1000)

    def switch_next_wallpaper(self):
        if not self.is_running:
            return
        if self.config.get("pause_on_games", True) and self.game_detector.is_game_running():
            return
        monitor = self.wm.get_next_monitor()
        if not monitor:
            return
        mid = monitor["id"]
        if self.config.get("pause_on_fullscreen", True):
            for hwnd in self.game_detector.get_fullscreen_windows():
                mon_rect = self.game_detector.get_monitor_of_window(hwnd)
                if mon_rect and mon_rect == monitor["rect"]:
                    return
        folder = self.get_current_main_folder()
        if not folder or not os.path.exists(folder):
            return
        img = ImageLoader.get_random_image(folder, recursive=True)
        if img:
            style = self.config.get("wallpaper_style", "fill")
            self.wm.set_wallpaper(mid, img, style)
            self.current_image = img
            self.current_monitor_id = mid

    def set_wallpaper_to_monitor(self, image_path, monitor_id):
        self.wm.set_wallpaper(monitor_id, image_path, self.config.get("wallpaper_style", "fill"))

    def like_current_wallpaper(self):
        if hasattr(self, 'current_image') and self.classifier:
            self.classifier.classify_image(self.current_image, 'like')
            QMessageBox.information(None, "成功", "已添加到喜欢列表")

    def dislike_current_wallpaper(self):
        if hasattr(self, 'current_image') and self.classifier:
            self.classifier.classify_image(self.current_image, 'dislike')
            QMessageBox.information(None, "成功", "已移动到不喜欢列表")

    def set_auto_start(self, enabled):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
            if enabled:
                exe = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
                winreg.SetValueEx(key, REG_KEY, 0, winreg.REG_SZ, f'"{exe}"')
            else:
                try:
                    winreg.DeleteValue(key, REG_KEY)
                except:
                    pass
            winreg.CloseKey(key)
            self.config["auto_start"] = enabled
            self.save_config()
        except Exception as e:
            print(f"设置开机启动失败: {e}")

    def toggle_visit_mode(self, enabled):
        self.visit_mode = enabled
        self.config["visit_mode"] = enabled
        self.save_config()
        self.init_classifier()
        msg = "已切换到访客模式" if enabled else "已退出访客模式"
        QMessageBox.information(None, "访客模式", msg)

    def open_settings(self):
        dlg = SettingsDialog(self.config)
        dlg.settings_saved.connect(self.on_settings_saved)
        dlg.exec_()

    def on_settings_saved(self, new_config):
        self.config = new_config
        self.save_config()
        self.update_timer_interval()
        self.game_detector.update_game_list(self.config.get("game_processes", []))
        self.register_hotkey()
        self.init_classifier()
        self.set_auto_start(self.config.get("auto_start", False))
        QMessageBox.information(None, "成功", "设置已应用")

    def open_browser(self):
        if not self.classifier:
            QMessageBox.warning(None, "提示", "请先在设置中配置主文件夹")
            return
        folder = self.get_current_main_folder()
        if not folder or not os.path.exists(folder):
            QMessageBox.warning(None, "提示", "当前图库文件夹不存在")
            return
        dlg = BrowserDialog(self.wm)
        dlg.wallpaper_selected.connect(self.set_wallpaper_to_monitor)
        dlg.exec_()

    def show_help(self):
        QMessageBox.information(None, "使用说明",
            "1. 右键托盘图标可进行各项操作\n"
            "2. 默认快捷键 Ctrl+Shift+W 立即切换壁纸\n"
            "3. 在设置中可自定义图库文件夹、切换间隔、壁纸样式等\n"
            "4. 开启游戏检测后，检测到指定游戏会暂停切换\n"
            "5. 访客模式会切换到独立的图库文件夹，不影响主图库\n"
            "6. 喜欢/不喜欢会自动归类图片\n"
            "7. 多屏轮流切换，每个屏幕独立壁纸")

    def register_hotkey(self):
        hotkey = self.config.get("hotkey", "ctrl+shift+w")
        self.hotkey_mgr.register_hotkey(hotkey, self.switch_next_wallpaper)

    def check_games(self):
        pass  # 实际检测在 switch_next_wallpaper 中已做

    def setup_signals(self):
        self.tray.signal_switch_now.connect(self.switch_next_wallpaper)
        self.tray.signal_like.connect(self.like_current_wallpaper)
        self.tray.signal_dislike.connect(self.dislike_current_wallpaper)
        self.tray.signal_toggle_auto_start.connect(self.set_auto_start)
        self.tray.signal_toggle_visit_mode.connect(self.toggle_visit_mode)
        self.tray.signal_open_browser.connect(self.open_browser)
        self.tray.signal_open_settings.connect(self.open_settings)
        self.tray.signal_show_help.connect(self.show_help)
        self.tray.signal_exit.connect(self.quit_app)

    def quit_app(self):
        self.is_running = False
        self.timer.stop()
        self.game_check_timer.stop()
        self.hotkey_mgr.cleanup()
        self.wm.cleanup()
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    changer = WallpaperChanger()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
