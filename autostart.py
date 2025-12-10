# autostart.py
import os
import sys
import platform

APP_NAME = "FileUploader"

def get_executable_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return os.path.abspath(sys.argv[0])

def enable_autostart():
    system = platform.system()
    exe = get_executable_path()
    if system == "Windows":
        import winreg
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, APP_NAME, 0, winreg.REG_SZ, exe)
    elif system == "Darwin":  # macOS
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.{APP_NAME.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.user.{APP_NAME.lower()}.plist")
        with open(plist_path, 'w') as f:
            f.write(plist_content)
    elif system == "Linux":
        desktop_entry = f"""[Desktop Entry]
Type=Application
Exec={exe}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name={APP_NAME}
"""
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        with open(os.path.join(autostart_dir, f"{APP_NAME}.desktop"), 'w') as f:
            f.write(desktop_entry)

def disable_autostart():
    system = platform.system()
    if system == "Windows":
        import winreg
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.DeleteValue(reg_key, APP_NAME)
        except FileNotFoundError:
            pass
    elif system == "Darwin":
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.user.{APP_NAME.lower()}.plist")
        if os.path.exists(plist_path):
            os.remove(plist_path)
    elif system == "Linux":
        desktop_path = os.path.expanduser(f"~/.config/autostart/{APP_NAME}.desktop")
        if os.path.exists(desktop_path):
            os.remove(desktop_path)