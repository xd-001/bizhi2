import configparser
import os
import json

DEFAULT_CONFIG = {
    "main_folder": os.path.expanduser("~/Pictures/Wallpapers"),
    "guest_folder": os.path.expanduser("~/Pictures/Wallpapers_Guest"),
    "switch_interval": 30,          # 秒
    "wallpaper_style": "fill",      # fill, fit, stretch, tile, center
    "transition_speed": 0,          # 未实现平滑过渡，占位
    "smooth_transition": False,
    "hotkey_modifiers": ["ctrl", "shift"],
    "hotkey_key": "w",
    "game_processes": ["game.exe", "eldenring.exe"],  # 示例
    "monitor_pause": {},             # 格式 {"\\\\.\\DISPLAY1": True, ...}
    "guest_mode": False,
    "auto_start": False
}

class ConfigManager:
    def __init__(self, config_path="config.ini"):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self):
        if not os.path.exists(self.config_path):
            self.set_defaults()
            self.save()
        else:
            self.config.read(self.config_path, encoding='utf-8')
            # 确保所有键存在
            for section, items in DEFAULT_CONFIG.items():
                if section not in self.config:
                    self.config[section] = {}
                for key, value in items.items():
                    if key not in self.config[section]:
                        self.config[section][key] = str(value)
            self.save()
    
    def set_defaults(self):
        for section, items in DEFAULT_CONFIG.items():
            self.config[section] = {}
            for key, value in items.items():
                self.config[section][key] = str(value)
    
    def save(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get(self, section, key, fallback=None):
        try:
            val = self.config[section][key]
            # 尝试转换类型
            default_val = DEFAULT_CONFIG.get(section, {}).get(key)
            if isinstance(default_val, bool):
                return val.lower() == 'true'
            if isinstance(default_val, int):
                return int(val)
            if isinstance(default_val, list):
                return eval(val) if val.startswith('[') else [x.strip() for x in val.strip('[]').split(',') if x]
            return val
        except:
            return fallback
    
    def set(self, section, key, value):
        self.config[section][key] = str(value)
        self.save()
