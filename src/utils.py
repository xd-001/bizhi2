import os
import shutil
from PIL import Image

def get_images_from_folder(folder):
    """递归获取文件夹下的所有图片文件"""
    extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    images = []
    if not os.path.exists(folder):
        return images
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(extensions):
                images.append(os.path.join(root, file))
    return images

def move_file_to_folder(file_path, target_folder):
    """将文件移动到目标文件夹（如喜欢/不喜欢）"""
    if not os.path.exists(file_path):
        return
    os.makedirs(target_folder, exist_ok=True)
    dest = os.path.join(target_folder, os.path.basename(file_path))
    shutil.move(file_path, dest)

def get_image_thumbnail(path, size=(128, 128)):
    """生成缩略图，失败返回None"""
    try:
        with Image.open(path) as img:
            img.thumbnail(size)
            return img
    except:
        return None
