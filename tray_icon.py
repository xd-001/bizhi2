# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal
import os
from constants import APP_NAME, BASE_DIR

class TrayIcon(QSystemTrayIcon):
    signal_switch_now = pyqtSignal()
    signal_like = pyqtSignal()
    signal_dislike = pyqtSignal()
    signal_toggle_auto_start = pyqtSignal(bool)
    signal_toggle_visit_mode = pyqtSignal(bool)
    signal_open_browser = pyqtSignal()
    signal_open_settings = pyqtSignal()
    signal_show_help = pyqtSignal()
    signal_exit = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = os.path.join(BASE_DIR, "icon.ico")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            self.setIcon(QIcon.fromTheme("application-x-executable"))
        self.setToolTip(APP_NAME)
        self._create_menu()
        self.auto_start = False
        self.visit_mode = False
        self.activated.connect(self._on_activated)

    def _create_menu(self):
        self.menu = QMenu()
        self.action_switch = QAction("⚡ 立即切换", self)
        self.action_switch.triggered.connect(self.signal_switch_now.emit)
        self.menu.addAction(self.action_switch)
        self.menu.addSeparator()
        self.action_like = QAction("❤️ 喜欢", self)
        self.action_like.triggered.connect(self.signal_like.emit)
        self.menu.addAction(self.action_like)
        self.action_dislike = QAction("💔 不喜欢", self)
        self.action_dislike.triggered.connect(self.signal_dislike.emit)
        self.menu.addAction(self.action_dislike)
        self.menu.addSeparator()
        self.action_auto_start = QAction("🔄 开机启动", self)
        self.action_auto_start.setCheckable(True)
        self.action_auto_start.triggered.connect(self._on_auto_start_toggled)
        self.menu.addAction(self.action_auto_start)
        self.action_visit_mode = QAction("👤 访客模式", self)
        self.action_visit_mode.setCheckable(True)
        self.action_visit_mode.triggered.connect(self._on_visit_mode_toggled)
        self.menu.addAction(self.action_visit_mode)
        self.menu.addSeparator()
        self.action_browser = QAction("🖼️ 图库浏览", self)
        self.action_browser.triggered.connect(self.signal_open_browser.emit)
        self.menu.addAction(self.action_browser)
        self.action_settings = QAction("⚙️ 设置", self)
        self.action_settings.triggered.connect(self.signal_open_settings.emit)
        self.menu.addAction(self.action_settings)
        self.action_help = QAction("📖 使用说明", self)
        self.action_help.triggered.connect(self.signal_show_help.emit)
        self.menu.addAction(self.action_help)
        self.menu.addSeparator()
        self.action_exit = QAction("🚪 退出", self)
        self.action_exit.triggered.connect(self.signal_exit.emit)
        self.menu.addAction(self.action_exit)
        self.setContextMenu(self.menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.signal_open_settings.emit()

    def _on_auto_start_toggled(self, checked):
        self.auto_start = checked
        self.signal_toggle_auto_start.emit(checked)

    def _on_visit_mode_toggled(self, checked):
        self.visit_mode = checked
        self.signal_toggle_visit_mode.emit(checked)

    def update_auto_start_state(self, enabled):
        self.auto_start = enabled
        self.action_auto_start.setChecked(enabled)

    def update_visit_mode_state(self, enabled):
        self.visit_mode = enabled
        self.action_visit_mode.setChecked(enabled)
