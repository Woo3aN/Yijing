"""易经占卜 —— PySide6 入口"""

import sys
import os
import ctypes

if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt

from ui.main_window import MainWindow
from storage.app_settings import load_settings


def _get_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        relative_path)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("易经占卜")

    # 全局默认字体 — 宋体有传统韵味
    font = QFont("宋体", 10)
    app.setFont(font)

    # 图标
    try:
        ico = _get_path("assets/icon.ico")
        if os.path.exists(ico):
            app.setWindowIcon(QIcon(ico))
    except Exception:
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
