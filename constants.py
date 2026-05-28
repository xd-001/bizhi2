# -*- coding: utf-8 -*-
import os
import sys

APP_NAME = "WallpaperChanger"
APP_VERSION = "1.0.0"

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_KEY = APP_NAME

DEFAULT_CONFIG = {
    "main_folder": os.path.expanduser("~/Pictures/Wallpapers"),
    "visit_folder": os.path.expanduser("~/Pictures/Wallpapers_Visit"),
    "interval": 30,
    "wallpaper_style": "fill",
    "smooth_transition": False,
    "transition_speed": 500,
    "hotkey": "ctrl+shift+w",
    "auto_start": False,
    "visit_mode": False,
    "game_processes": ["csgo.exe", "League of Legends.exe", "GTA5.exe"],
    "pause_on_fullscreen": True,
    "pause_on_games": True,
    "screen_pause": {}
}

STYLE_MAP = {
    "fill": 0,
    "fit": 1,
    "stretch": 2,
    "tile": 3,
    "center": 4
}

DIR_DEFAULT = "默认"
DIR_LIKE = "喜欢"
DIR_DISLIKE = "不喜欢"

BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
