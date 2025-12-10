# main.py
# main.py
# ============ 单例保护（必须放在最前面！）============
# main.py
# ============ 单例保护（必须放在最前面！）============
# main.py
# ============ 单例保护（必须放在最前面！）============
import sys
import os

from tendo import singleton
from tendo.singleton import SingleInstanceException
# 尝试创建单例
try:
    me = singleton.SingleInstance()
except SingleInstanceException:
    # ========== 已有实例运行，弹窗提示并退出 ==========
        import tkinter as tk
        from tkinter import messagebox

        # 创建临时 Tk 窗口用于弹窗
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        messagebox.showwarning(
            "程序已在运行",
            "文件上传助手已经在运行中。\n\n请在系统托盘中操作，无需重复启动。"
        )
        root.destroy()
        sys.exit(0)  # 正常退出，不报错
# ====================================================

import os
import sys
import json
import time
import threading
import logging
import traceback

# 日志配置
LOG_FILE = 'uploader.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

CONFIG_FILE = 'config.json'

# === 必须在主线程初始化 Tk（macOS 要求）===
import tkinter as tk
import queue

root_tk = tk.Tk()
root_tk.withdraw()  # 隐藏主窗口
gui_queue = queue.Queue()
# ==========================================

# 尝试导入托盘
try:
    from tray_icon import create_tray_icon
    HAS_TRAY = True
except Exception as e:
    logging.warning(f"⚠️ 托盘不可用: {e}")
    HAS_TRAY = False

# --- 业务逻辑 ---
def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "tenantId": "",
            "orgId": "",
            "uploadUrl": "https://example.com/upload",
            "watchPath": "",
            "movePath": "",
            "fileExtensions": ".pdf",
            "rule": "_",
            "position": "0",
            "level": 1,
            "serviceCode": "",
            "autoStart": False
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        logging.info("✅ 生成默认配置文件 config.json")
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def upload_file(filepath, config):
    filename = os.path.basename(filepath)
    try:
        rule = config.get('rule', '_')
        position = int(config.get('position', '0'))
        parts = filename.split(rule)
        if position >= len(parts):
            raise ValueError(f"位置 {position} 超出分割长度 {len(parts)}")
        visit_number = parts[position]
    except Exception as e:
        logging.error(f"❌ 文件名解析失败 ({filename}): {e}")
        return False

    try:
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f)}
            data = {
                'tenantId': config['tenantId'],
                'orgId': config.get('orgId', ''),
                'visitNumber': visit_number,
                'serviceCode': config['serviceCode']
            }
            import requests
            resp = requests.post(config['uploadUrl'], data=data, files=files, timeout=60)
            result = resp.json()
            if result.get('head', {}).get('errCode') == 0 and result.get('data') == 'success':
                logging.info(f"✅ 上传成功: {filename}")
                move_path = config.get('movePath')
                if move_path and os.path.isdir(move_path):
                    import shutil
                    dest = os.path.join(move_path, filename)
                    shutil.move(filepath, dest)
                    logging.info(f"📁 移动至: {dest}")
                return True
            else:
                logging.error(f"❌ 上传失败 ({filename}): {result}")
                return False
    except Exception as e:
        logging.exception(f"⚠️ 上传异常 ({filename}): {e}")
        return False

class FileUploader:
    def __init__(self):
        self.observer = None
        self.running = False

    def _run(self):
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class Handler(FileSystemEventHandler):
            def __init__(self, config):
                self.config = config
            def on_created(self, event):
                if not event.is_directory:
                    filepath = event.src_path
                    exts = [e.strip().lower() for e in self.config.get('fileExtensions', '').split(',') if e.strip()]
                    if exts and not any(filepath.lower().endswith(ext) for ext in exts):
                        return
                    logging.info(f"📥 检测到新文件: {filepath}")
                    upload_file(filepath, self.config)

        while True:
            config = load_config()
            watch_path = config.get('watchPath', '').strip()
            if not watch_path or not os.path.isdir(watch_path):
                logging.warning("⚠️ 监听路径无效，等待配置...")
                time.sleep(5)
                continue
            break

        level = config.get('level', 1)
        recursive = level > 0
        event_handler = Handler(config)
        self.observer = Observer()
        try:
            self.observer.schedule(event_handler, watch_path, recursive=recursive)
            self.observer.start()
            self.running = True
            logging.info(f"👀 开始监听: {watch_path} (递归: {recursive})")
        except Exception as e:
            logging.error(f"❌ 监听异常: {e}")
        finally:
            if self.observer:
                self.observer.stop()
                self.observer.join()

    def start(self):
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def stop(self):
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        logging.info("⏹️ 监听已停止")

# === GUI 任务处理 ===
def process_gui_tasks():
    try:
        while True:
            task = gui_queue.get_nowait()
            if task == "open_config":
                from config_gui import open_config_window
                open_config_window()
    except queue.Empty:
        pass
    root_tk.after(100, process_gui_tasks)
# ====================

def main():
    uploader = FileUploader()
    uploader.start()

    tray_icon = None
    if HAS_TRAY:
        logging.info("🖥️ 启动系统托盘图标（主线程）...")
        try:
            tray_icon = create_tray_icon(uploader, gui_queue)
        except Exception as e:
            logging.error(f"❌ 托盘启动失败: {e}")
            traceback.print_exc()

    root_tk.after(100, process_gui_tasks)
    try:
        root_tk.mainloop()
    except KeyboardInterrupt:
        logging.info("⏹️ 收到中断信号")
    finally:
        if tray_icon:
            tray_icon.stop()
        uploader.stop()
        os._exit(0)

if __name__ == '__main__':
    main()