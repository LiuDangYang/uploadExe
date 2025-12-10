# config_gui.py
import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

CONFIG_FILE = 'config.json'

# 全局窗口实例（确保单例）
_config_window_instance = None


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def select_folder(entry_widget):
    folder = filedialog.askdirectory()
    if folder:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder)


def bring_window_to_front(win):
    """将窗口带到最前（macOS + Windows 兼容）"""
    if sys.platform == "darwin":
        try:
            script = f'tell application "System Events" to set frontmost of (first process whose unix id is {os.getpid()}) to true'
            subprocess.run(['osascript', '-e', script],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        except Exception:
            pass  # 失败则忽略

    win.lift()
    win.focus_force()
    win.attributes('-topmost', True)
    win.after(150, lambda: win.attributes('-topmost', False))


def on_config_window_close(window):
    global _config_window_instance
    _config_window_instance = None
    window.destroy()


def open_config_window():
    global _config_window_instance

    # 如果窗口已存在，直接唤到前台
    if _config_window_instance is not None and _config_window_instance.winfo_exists():
        bring_window_to_front(_config_window_instance)
        return

    config = load_config()

    win = tk.Toplevel()
    win.title("上传配置")
    win.geometry("700x500")
    win.resizable(False, False)
    win.withdraw()  # 先隐藏，避免闪烁

    _config_window_instance = win
    win.protocol("WM_DELETE_WINDOW", lambda: on_config_window_close(win))

    canvas = tk.Canvas(win)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    entries = {}

    fields = [
        ("租户ID (tenantId)", "tenantId"),
        ("机构ID (orgId)", "orgId"),
        ("上传地址 (uploadUrl)", "uploadUrl"),
        ("监听路径 (watchPath)", "watchPath"),
        ("移动路径 (movePath)", "movePath"),
        ("文件扩展名 (如 .pdf,.jpg)", "fileExtensions"),
        ("分割规则 (如 _)", "rule"),
        ("取第几段 (从0开始)", "position"),
        ("递归层级 (0=不递归)", "level"),
        ("服务编码 (serviceCode)", "serviceCode"),
    ]

    for i, (label_text, key) in enumerate(fields):
        ttk.Label(scrollable_frame, text=label_text).grid(row=i, column=0, sticky="w", padx=10, pady=5)
        entry = ttk.Entry(scrollable_frame, width=40)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entry.insert(0, config.get(key, ""))
        entries[key] = entry

        if key in ["watchPath", "movePath"]:
            btn = ttk.Button(scrollable_frame, text="选择",
                             command=lambda e=entry: select_folder(e))
            btn.grid(row=i, column=2, padx=5)

    auto_start_var = tk.BooleanVar(value=config.get("autoStart", False))
    ttk.Checkbutton(scrollable_frame, text="开机自启", variable=auto_start_var).grid(
        row=len(fields), column=0, columnspan=2, sticky="w", padx=10, pady=10)

    def save_and_close():
        data = {key: entry.get().strip() for key, entry in entries.items()}
        data["autoStart"] = auto_start_var.get()
        try:
            data["position"] = str(int(data.get("position", "0")))
            data["level"] = int(data.get("level", "1"))
        except ValueError:
            messagebox.showerror("错误", "位置和层级必须是整数！")
            return
        save_config(data)
        on_config_window_close(win)
        messagebox.showinfo("提示", "配置已保存！")

    btn_frame = ttk.Frame(scrollable_frame)
    btn_frame.grid(row=len(fields) + 1, column=0, columnspan=3, pady=20)
    ttk.Button(btn_frame, text="保存并关闭", command=save_and_close).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="取消", command=lambda: on_config_window_close(win)).pack(side=tk.LEFT, padx=10)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 居中显示
    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_reqwidth()) // 2
    y = (win.winfo_screenheight() - win.winfo_reqheight()) // 2
    win.geometry(f"+{x}+{y}")
    win.deiconify()

    bring_window_to_front(win)