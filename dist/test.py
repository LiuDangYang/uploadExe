import pystray
from PIL import Image, ImageDraw
import threading


# 模拟打开配置窗口的函数
def open_config_window():
    print("配置窗口应该在这里打开")
    # 在此处放置实际打开配置窗口的代码
    # 例如：可以启动一个新的线程来显示GUI窗口等


# 创建托盘图标图像
def create_image():
    # 生成一个简单的蓝色方形图像作为托盘图标
    width, height = 64, 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (16, 16, width - 16, height - 16),
        fill='blue')
    return image


# 定义当图标被点击时的行为
def on_clicked(icon, item):
    # 调用打开配置窗口的函数
    open_config_window()


# 设置并运行托盘图标
def setup_tray_icon():
    # 创建菜单项
    menu = (
        pystray.MenuItem('配置', on_clicked, default=True),  # 默认项，单击图标时触发
        pystray.MenuItem('退出', lambda icon, item: icon.stop()),  # 退出选项
    )

    # 创建托盘图标实例
    tray_icon = pystray.Icon("name", create_image(), "My System Tray Icon", menu)

    # 运行托盘图标
    tray_icon.run()


if __name__ == "__main__":
    # 使用线程运行托盘图标，以便不会阻塞其他操作
    tray_thread = threading.Thread(target=setup_tray_icon)
    tray_thread.start()

    # 可以在此处添加其他代码逻辑