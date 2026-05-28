# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QScrollArea,
                             QLabel, QWidget, QPushButton, QFileDialog,
                             QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import os
from wallpaper_manager import ImageLoader

class ImageThumbnail(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setFixedSize(200, 150)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel { border: 2px solid #ccc; border-radius: 5px; padding: 5px; background-color: #f5f5f5; }
            QLabel:hover { border-color: #4CAF50; background-color: #e8f5e9; }
        """)
        self.load_thumbnail()

    def load_thumbnail(self):
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(190, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path)


class BrowserDialog(QDialog):
    wallpaper_selected = pyqtSignal(str, str)

    def __init__(self, wallpaper_manager, parent=None):
        super().__init__(parent)
        self.wm = wallpaper_manager
        self.current_folder = ""
        self.thumbnails = []
        self.setWindowTitle("图库浏览")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        control = QGridLayout()
        self.btn_select = QPushButton("选择文件夹")
        self.btn_select.clicked.connect(self.select_folder)
        control.addWidget(self.btn_select, 0, 0)
        self.label_folder = QLabel("未选择文件夹")
        control.addWidget(self.label_folder, 0, 1)
        control.addWidget(QLabel("设置到显示器:"), 1, 0)
        self.combo_monitor = QComboBox()
        self.refresh_monitors()
        control.addWidget(self.combo_monitor, 1, 1)
        layout.addLayout(control)

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def refresh_monitors(self):
        self.combo_monitor.clear()
        for mon in self.wm.monitors:
            self.combo_monitor.addItem(f"显示器 {mon['index']+1}", mon["id"])

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图库文件夹")
        if folder:
            self.current_folder = folder
            self.label_folder.setText(folder)
            self.load_images(folder)

    def load_images(self, folder):
        for thumb in self.thumbnails:
            thumb.deleteLater()
        self.thumbnails.clear()
        images = ImageLoader.get_images_from_folder(folder, recursive=True)
        if not images:
            label = QLabel("该文件夹中没有图片")
            label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(label, 0, 0)
            return
        row = col = 0
        max_cols = 4
        for img in images:
            thumb = ImageThumbnail(img)
            thumb.clicked.connect(self.on_image_clicked)
            self.grid_layout.addWidget(thumb, row, col)
            self.thumbnails.append(thumb)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def on_image_clicked(self, image_path):
        monitor_id = self.combo_monitor.currentData()
        if monitor_id:
            reply = QMessageBox.question(self, "确认", "是否将此图片设为壁纸？", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.wallpaper_selected.emit(image_path, monitor_id)
                self.accept()
