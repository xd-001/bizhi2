# -*- coding: utf-8 -*-
import threading
import keyboard
from typing import Callable

class HotkeyManager:
    def __init__(self):
        self.hotkey = None
        self.callback = None
        self.is_registered = False

    def register_hotkey(self, hotkey: str, callback: Callable):
        self.unregister_hotkey()
        try:
            self.hotkey = hotkey
            self.callback = callback
            keyboard.add_hotkey(hotkey, self._on_hotkey)
            self.is_registered = True
        except Exception as e:
            print(f"注册热键失败: {e}")

    def unregister_hotkey(self):
        if self.is_registered and self.hotkey:
            try:
                keyboard.remove_hotkey(self.hotkey)
            except:
                pass
            self.is_registered = False

    def _on_hotkey(self):
        if self.callback:
            threading.Thread(target=self.callback, daemon=True).start()

    def cleanup(self):
        self.unregister_hotkey()
