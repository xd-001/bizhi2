# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QWidget, QLabel, QLineEdit, QPushButton,
                             QFileDialog, QSlider, QComboBox, QCheckBox,
                             QListWidget, QMessageBox, QGroupBox, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal(dict)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.setWindowTitle("设置")
        self.setMinimumSize(500, 600)
        self.init_ui()
        self.load_config()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_basic_tab(), "基本设置")
        self.tab_widget.addTab(self.create_wallpaper_tab(), "壁纸设置")
        self.tab_widget.addTab(self.create_game_tab(), "游戏检测")
        self.tab_widget.addTab(self.create_hotkey_tab(), "快捷键")
        layout.addWidget(self.tab_widget)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("保存")
        btn_save.clicked.connect(self.save_settings)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def create_basic_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        group = QGroupBox("图库设置")
        gl = QVBoxLayout()
        fl = QHBoxLayout()
        fl.addWidget(QLabel("主文件夹:"))
        self.edit_main = QLineEdit()
        fl.addWidget(self.edit_main)
        btn1 = QPushButton("浏览")
        btn1.clicked.connect(lambda: self.browse_folder(self.edit_main))
        fl.addWidget(btn1)
        gl.addLayout(fl)
        fl2 = QHBoxLayout()
        fl2.addWidget(QLabel("访客文件夹:"))
        self.edit_visit = QLineEdit()
        fl2.addWidget(self.edit_visit)
        btn2 = QPushButton("浏览")
        btn2.clicked.connect(lambda: self.browse_folder(self.edit_visit))
        fl2.addWidget(btn2)
        gl.addLayout(fl2)
        group.setLayout(gl)
        layout.addWidget(group)

        group2 = QGroupBox("切换间隔")
        gl2 = QVBoxLayout()
        hl = QHBoxLayout()
        hl.addWidget(QLabel("间隔时间(秒):"))
        self.slider_int = QSlider(Qt.Horizontal)
        self.slider_int.setRange(5, 300)
        self.label_int = QLabel("30")
        self.slider_int.valueChanged.connect(lambda v: self.label_int.setText(str(v)))
        hl.addWidget(self.slider_int)
        hl.addWidget(self.label_int)
        gl2.addLayout(hl)
        preset = QHBoxLayout()
        for p in [10, 30, 60, 120]:
            btn = QPushButton(f"{p}秒")
            btn.clicked.connect(lambda checked, val=p: self.slider_int.setValue(val))
            preset.addWidget(btn)
        gl2.addLayout(preset)
        group2.setLayout(gl2)
        layout.addWidget(group2)
        layout.addStretch()
        w.setLayout(layout)
        return w

    def create_wallpaper_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        hl = QHBoxLayout()
        hl.addWidget(QLabel("壁纸样式:"))
        self.combo_style = QComboBox()
        self.combo_style.addItems(["填充", "适应", "拉伸", "平铺", "居中"])
        hl.addWidget(self.combo_style)
        layout.addLayout(hl)
        self.check_smooth = QCheckBox("启用平滑过渡")
        self.check_smooth.toggled.connect(self.on_smooth_toggled)
        layout.addWidget(self.check_smooth)
        hl2 = QHBoxLayout()
        hl2.addWidget(QLabel("过渡速度(毫秒):"))
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(100, 2000)
        self.label_speed = QLabel("500")
        self.slider_speed.valueChanged.connect(lambda v: self.label_speed.setText(str(v)))
        hl2.addWidget(self.slider_speed)
        hl2.addWidget(self.label_speed)
        layout.addLayout(hl2)
        self.check_screen_pause = QCheckBox("每屏幕独立暂停（检测到全屏时跳过）")
        layout.addWidget(self.check_screen_pause)
        layout.addStretch()
        w.setLayout(layout)
        return w

    def create_game_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        self.check_pause_games = QCheckBox("检测到游戏时暂停切换")
        layout.addWidget(self.check_pause_games)
        layout.addWidget(QLabel("游戏进程名列表:"))
        self.list_games = QListWidget()
        layout.addWidget(self.list_games)
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("添加")
        btn_add.clicked.connect(self.add_game_process)
        btn_remove = QPushButton("删除")
        btn_remove.clicked.connect(self.remove_game_process)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)
        layout.addStretch()
        w.setLayout(layout)
        return w

    def create_hotkey_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("快捷键组合:"))
        self.edit_hotkey = QLineEdit()
        self.edit_hotkey.setPlaceholderText("例如: ctrl+shift+w")
        layout.addWidget(self.edit_hotkey)
        layout.addWidget(QLabel("提示: 支持ctrl, shift, alt, win + 字母/数字/功能键"))
        layout.addStretch()
        w.setLayout(layout)
        return w

    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            line_edit.setText(folder)

    def add_game_process(self):
        proc, ok = QInputDialog.getText(self, "添加进程", "请输入进程名(例如: csgo.exe):")
        if ok and proc:
            self.list_games.addItem(proc)

    def remove_game_process(self):
        cur = self.list_games.currentRow()
        if cur >= 0:
            self.list_games.takeItem(cur)

    def on_smooth_toggled(self, checked):
        self.slider_speed.setEnabled(checked)
        if checked:
            QMessageBox.information(self, "提示", "平滑过渡功能由于系统限制，当前版本可能无法达到理想效果。")

    def load_config(self):
        self.edit_main.setText(self.config.get("main_folder", ""))
        self.edit_visit.setText(self.config.get("visit_folder", ""))
        self.slider_int.setValue(self.config.get("interval", 30))
        style_map = {"fill":0, "fit":1, "stretch":2, "tile":3, "center":4}
        self.combo_style.setCurrentIndex(style_map.get(self.config.get("wallpaper_style","fill"),0))
        self.check_smooth.setChecked(self.config.get("smooth_transition",False))
        self.slider_speed.setValue(self.config.get("transition_speed",500))
        self.check_screen_pause.setChecked(self.config.get("pause_on_fullscreen",True))
        self.check_pause_games.setChecked(self.config.get("pause_on_games",True))
        self.edit_hotkey.setText(self.config.get("hotkey","ctrl+shift+w"))
        self.list_games.clear()
        for g in self.config.get("game_processes", []):
            self.list_games.addItem(g)

    def save_settings(self):
        self.config["main_folder"] = self.edit_main.text()
        self.config["visit_folder"] = self.edit_visit.text()
        self.config["interval"] = self.slider_int.value()
        rev = {0:"fill",1:"fit",2:"stretch",3:"tile",4:"center"}
        self.config["wallpaper_style"] = rev.get(self.combo_style.currentIndex(),"fill")
        self.config["smooth_transition"] = self.check_smooth.isChecked()
        self.config["transition_speed"] = self.slider_speed.value()
        self.config["pause_on_fullscreen"] = self.check_screen_pause.isChecked()
        self.config["pause_on_games"] = self.check_pause_games.isChecked()
        self.config["hotkey"] = self.edit_hotkey.text()
        games = [self.list_games.item(i).text() for i in range(self.list_games.count())]
        self.config["game_processes"] = games
        self.settings_saved.emit(self.config)
        self.accept()
        QMessageBox.information(self, "成功", "设置已保存并立即生效")
