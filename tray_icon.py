# tray_icon.py
import os
import sys
from PIL import Image
from pystray import Icon as SysTrayIcon, Menu as SysTrayMenu, MenuItem as SysTrayMenuItem


def load_tray_icon():
    """加载自定义托盘图标（支持开发模式和打包）"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(base_path,   'icon.png')

    if os.path.exists(icon_path):
        try:
            return Image.open(icon_path).convert("RGBA")
        except Exception as e:
            print(f"⚠️ 无法加载图标 {icon_path}: {e}")

    return create_default_icon()


def create_default_icon():
    """备用：生成默认图标"""
    from PIL import ImageDraw
    width, height = 64, 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((8, 8, 56, 56), fill=(70, 130, 180))  # SteelBlue
    dc.ellipse((20, 20, 44, 44), fill=(255, 255, 255))
    return image


def create_tray_icon(uploader, gui_queue=None):
    def on_show_config(icon, item):
        if gui_queue is not None:
            gui_queue.put("open_config")

    def on_quit(icon, item):
        uploader.stop()
        icon.stop()
        os._exit(0)

    menu = SysTrayMenu(
        SysTrayMenuItem('打开配置', on_show_config),
        SysTrayMenuItem('退出', on_quit)
    )

    icon_image = load_tray_icon()

    icon = SysTrayIcon(
        name="FileUploader",
        title="文件上传助手",
        menu=menu,
        icon=icon_image
    )

    icon.run_detached()
    return icon