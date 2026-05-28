# -*- coding: utf-8 -*-
import os
import shutil
from constants import DIR_DEFAULT, DIR_LIKE, DIR_DISLIKE

class FileClassifier:
    def __init__(self, base_folder: str):
        self.base_folder = base_folder
        self._ensure_directories()

    def _ensure_directories(self):
        for dir_name in [DIR_DEFAULT, DIR_LIKE, DIR_DISLIKE]:
            os.makedirs(os.path.join(self.base_folder, dir_name), exist_ok=True)

    def get_folder_path(self, category: str) -> str:
        return os.path.join(self.base_folder, category)

    def classify_image(self, image_path: str, action: str):
        if not os.path.exists(image_path):
            return None
        if action == 'like':
            target_dir = self.get_folder_path(DIR_LIKE)
        elif action == 'dislike':
            target_dir = self.get_folder_path(DIR_DISLIKE)
        else:
            target_dir = self.get_folder_path(DIR_DEFAULT)

        if os.path.dirname(image_path) == target_dir:
            return image_path

        filename = os.path.basename(image_path)
        new_path = os.path.join(target_dir, filename)
        counter = 1
        while os.path.exists(new_path):
            name, ext = os.path.splitext(filename)
            new_path = os.path.join(target_dir, f"{name}_{counter}{ext}")
            counter += 1
        try:
            shutil.move(image_path, new_path)
            return new_path
        except Exception as e:
            print(f"移动文件失败: {e}")
            return None
