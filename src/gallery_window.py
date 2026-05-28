import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
import os
from utils import get_images_from_folder, get_image_thumbnail
from config_manager import ConfigManager

def open_gallery(config: ConfigManager):
    win = tk.Toplevel()
    win.title("图库浏览")
    win.geometry("800x600")

    folder = config.get("general", "main_folder")
    images = get_images_from_folder(folder)

    canvas = tk.Canvas(win)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scrollable = ttk.Frame(canvas)
    scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def set_as_wallpaper(img_path):
        # 简化：此处可以调用 WallpaperManager 的方法，但为了避免循环导入，先打印
        print("设置壁纸:", img_path)
        win.destroy()

    row, col = 0, 0
    for img_path in images:
        thumb = get_image_thumbnail(img_path)
        if thumb:
            photo = ImageTk.PhotoImage(thumb)
            btn = tk.Button(scrollable, image=photo, command=lambda path=img_path: set_as_wallpaper(path))
            btn.image = photo
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col >= 4:
                col = 0
                row += 1

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    win.mainloop()
