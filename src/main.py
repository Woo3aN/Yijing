"""易经占卜 —— 程序入口"""

import ctypes
import sys
import os
import tkinter as tk

# 高 DPI 适配（Windows）
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from ui.main_window import MainWindow


def _get_path(relative_path: str) -> str:
    """获取资源路径，兼容开发模式和 PyInstaller 打包"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        relative_path)


def main():
    # 创建主窗口，使用 darkly 深色主题
    root = ttk.Window(
        themename="darkly",
        title="易经占卜",
        size=(960, 740),
        minsize=(720, 540),
    )

    # 设置八卦图标（双保险：iconbitmap + iconphoto）
    try:
        ico_path = _get_path("assets/icon.ico")
        png_path = _get_path("assets/icon.png")
        if os.path.exists(ico_path):
            root.iconbitmap(ico_path)
        if os.path.exists(png_path):
            icon_img = tk.PhotoImage(file=png_path)
            root.iconphoto(True, icon_img)
            root._icon_image = icon_img  # 防止被垃圾回收
    except Exception:
        pass

    # 设置全局默认字体
    default_font = ("等线", 10)
    root.option_add("*Font", default_font)

    # 启动主界面
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
