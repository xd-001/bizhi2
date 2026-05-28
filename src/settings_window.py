import tkinter as tk
from tkinter import ttk, messagebox
from config_manager import ConfigManager
from wallpaper_manager import WallpaperManager

def open_settings(config: ConfigManager, manager: WallpaperManager):
    win = tk.Toplevel()
    win.title("设置")
    win.geometry("500x400")

    notebook = ttk.Notebook(win)
    notebook.pack(fill='both', expand=True)

    # 基本设置页
    basic = ttk.Frame(notebook)
    notebook.add(basic, text="基本")

    tk.Label(basic, text="主文件夹:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    main_var = tk.StringVar(value=config.get("general", "main_folder"))
    tk.Entry(basic, textvariable=main_var, width=40).grid(row=0, column=1, padx=5)
    def save_main():
        config.set("general", "main_folder", main_var.get())
    tk.Button(basic, text="保存", command=save_main).grid(row=0, column=2)

    tk.Label(basic, text="切换间隔(秒):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
    interval_var = tk.IntVar(value=config.get("general", "switch_interval"))
    tk.Scale(basic, from_=10, to=300, orient='horizontal', variable=interval_var).grid(row=1, column=1, sticky='ew')
    def save_interval():
        config.set("general", "switch_interval", interval_var.get())
        manager.stop()
        manager.start_rotation()
    tk.Button(basic, text="保存", command=save_interval).grid(row=1, column=2)

    tk.Label(basic, text="游戏进程(逗号分隔):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
    game_var = tk.StringVar(value=",".join(config.get("general", "game_processes")))
    tk.Entry(basic, textvariable=game_var, width=40).grid(row=2, column=1, padx=5)
    def save_game():
        processes = [p.strip() for p in game_var.get().split(',') if p.strip()]
        config.set("general", "game_processes", processes)
    tk.Button(basic, text="保存", command=save_game).grid(row=2, column=2)

    # 访客模式页
    guest = ttk.Frame(notebook)
    notebook.add(guest, text="访客")
    tk.Label(guest, text="访客文件夹:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    guest_var = tk.StringVar(value=config.get("general", "guest_folder"))
    tk.Entry(guest, textvariable=guest_var, width=40).grid(row=0, column=1, padx=5)
    def save_guest():
        config.set("general", "guest_folder", guest_var.get())
    tk.Button(guest, text="保存", command=save_guest).grid(row=0, column=2)

    # 快捷键页
    hotkey = ttk.Frame(notebook)
    notebook.add(hotkey, text="快捷键")
    tk.Label(hotkey, text="修饰键(ctrl,alt,shift,win):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    mod_var = tk.StringVar(value="+".join(config.get("hotkey", "hotkey_modifiers")))
    tk.Entry(hotkey, textvariable=mod_var, width=30).grid(row=0, column=1)
    tk.Label(hotkey, text="主键:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
    key_var = tk.StringVar(value=config.get("hotkey", "hotkey_key"))
    tk.Entry(hotkey, textvariable=key_var, width=10).grid(row=1, column=1, sticky='w')
    def save_hotkey():
        mods = mod_var.get().split('+')
        config.set("hotkey", "hotkey_modifiers", mods)
        config.set("hotkey", "hotkey_key", key_var.get())
        messagebox.showinfo("提示", "快捷键已保存，请重启程序生效")
    tk.Button(hotkey, text="保存", command=save_hotkey).grid(row=2, column=0, columnspan=2, pady=10)

    win.mainloop()
