import pystray
from PIL import Image, ImageDraw


def create_image():
    # 创建一个64x64像素的图像，颜色为蓝色
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), "blue")
    dc = ImageDraw.Draw(image)

    # 在图像上画一个白色的圆
    dc.ellipse((10, 10, 54, 54), fill="white")
    return image


def setup(icon, item):
    icon.update_menu()


def exit_action(icon, item):
    icon.stop()


# 创建图标
icon = pystray.Icon("test_icon", create_image(), "My Icon",
                    menu=pystray.Menu(
                        pystray.MenuItem("设置", setup),
                        pystray.MenuItem("退出", exit_action)
                    ))

# 运行图标
icon.run()