"""主窗口 —— PySide6 + 全局 QSS + 深/浅主题"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QApplication,
)
from PySide6.QtCore import Qt

from .divination_page import DivinationPage
from .history_page import HistoryPage
from .settings_page import SettingsPage
from storage.app_settings import load_settings, save_settings


# ═══════════════════════════════════
#  深色主题 QSS
# ═══════════════════════════════════
DARK_QSS = """
/* ── 全局 ── */
QMainWindow, QWidget {
    background-color: #161511; color: #f0ece0;
    font-family: 宋体, SimSun, serif; font-size: 13px;
}

/* ── 导航按钮 ── */
QPushButton#NavBtn {
    background: #1e1d18; color: #9b9788; border: 1px solid #2e2c24;
    border-radius: 10px; padding: 8px 24px; font-size: 14px; font-weight: bold;
    min-width: 80px; font-family: 宋体;
}
QPushButton#NavBtn:hover { background: #2a2820; color: #ca8a04; border-color: #ca8a04; }
QPushButton#NavBtn:checked, QPushButton#NavBtn[active="true"] {
    background: #ca8a04; color: #161511; border-color: #ca8a04;
}

/* ── 主要按钮 ── */
QPushButton#primaryBtn, QPushButton#warnBtn {
    background: #ca8a04; color: #ffffff; border: none;
    border-radius: 10px; padding: 10px 24px; font-size: 14px; font-weight: bold;
    font-family: 宋体;
}
QPushButton#primaryBtn:hover, QPushButton#warnBtn:hover { background: #e09e08; }
QPushButton#primaryBtn:disabled, QPushButton#warnBtn:disabled {
    background: #3d342b; color: #5e5a4e;
}
QPushButton#successBtn {
    background: #0d9488; color: #ffffff; border: none;
    border-radius: 10px; padding: 10px 24px; font-size: 14px; font-weight: bold;
    font-family: 宋体;
}
QPushButton#successBtn:hover { background: #0faaa0; }
QPushButton#successBtn:disabled { background: #1a3d38; color: #5e5a4e; }

/* ── 描边按钮 ── */
QPushButton#outlineBtn {
    background: transparent; color: #ca8a04; border: 1px solid #ca8a04;
    border-radius: 10px; padding: 8px 20px; font-size: 12px;
    font-family: 宋体;
}
QPushButton#outlineBtn:hover { background: rgba(202,138,4,0.1); }

/* ── 危险按钮 ── */
QPushButton#dangerBtn {
    background: #c44a4a; color: #ffffff; border: none;
    border-radius: 10px; padding: 8px 20px; font-size: 12px; font-family: 宋体;
}
QPushButton#dangerBtn:hover { background: #d44a4a; }
QPushButton#dangerOutBtn {
    background: transparent; color: #c44a4a; border: 1px solid #c44a4a;
    border-radius: 10px; padding: 8px 20px; font-size: 12px; font-family: 宋体;
}
QPushButton#dangerOutBtn:hover { background: rgba(196,74,74,0.1); }
QPushButton#dangerOutBtn:disabled { color: #5e5a4e; border-color: #3d342b; }

/* ── 主题切换按钮 ── */
QPushButton#themeDark, QPushButton#themeLight {
    background: #1e1d18; color: #9b9788; border: 1px solid #2e2c24;
    border-radius: 10px; padding: 6px 16px; font-size: 12px; font-family: 宋体;
}
QPushButton#themeDark:checked, QPushButton#themeLight:checked {
    background: #ca8a04; color: #161511; border-color: #ca8a04;
}

/* ── 卡片 ── */
QFrame#card { background: #1e1d18; border: 1px solid #2e2c24; border-radius: 12px; }

/* ── 卡片标题 ── */
QLabel#cardTitle { color: #f0ece0; font-size: 14px; font-weight: bold; font-family: 宋体; }
QLabel#cardSubTitle { color: #9b9788; font-size: 12px; font-weight: bold; font-family: 宋体; }
QLabel#statusLabel { color: #9b9788; font-size: 12px; font-family: 宋体; }
QLabel#detailTitle { color: #f0ece0; font-size: 14px; font-weight: bold; font-family: 宋体; }
QLabel#hintLabel { color: #9b9788; font-size: 12px; font-family: 宋体; }

/* ── 输入框 / 文本编辑 ── */
QTextEdit, QPlainTextEdit {
    background: #161511; color: #f0ece0; border: 1px solid #2e2c24;
    border-radius: 8px; padding: 12px; font-size: 14px; font-family: 宋体;
}
QTextEdit:focus, QPlainTextEdit:focus { border-color: #ca8a04; }
QLineEdit {
    background: #161511; color: #f0ece0; border: 1px solid #2e2c24;
    border-radius: 8px; padding: 10px; font-size: 13px; font-family: 宋体;
}
QLineEdit:focus { border-color: #ca8a04; }

/* ── 下拉框 ── */
QComboBox {
    background: #161511; color: #f0ece0; border: 1px solid #2e2c24;
    border-radius: 8px; padding: 8px; font-size: 13px; font-family: 宋体;
}
QComboBox:hover { border-color: #ca8a04; }
QComboBox::drop-down { border: none; border-radius: 8px; subcontrol-origin: padding; subcontrol-position: top right; width: 24px; }
QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 7px solid #9b9788; margin-right: 8px; }
QComboBox QAbstractItemView {
    background: #1e1d18; color: #f0ece0;
    selection-background-color: #ca8a04; selection-color: #161511;
}

/* ── 表格 ── */
QTableWidget {
    background: #161511; color: #f0ece0; border: 1px solid #2e2c24;
    border-radius: 8px; gridline-color: #2e2c24; font-family: 宋体;
}
QTableWidget::item { padding: 8px 12px; }
QTableWidget::item:selected { background: #ca8a04; color: #161511; }
QHeaderView::section {
    background: #1e1d18; color: #9b9788; padding: 8px;
    border: none; border-bottom: 1px solid #2e2c24; font-weight: bold; font-family: 宋体;
}

/* ── 标签 ── */
QLabel { background: transparent; border: none; }

/* ── 设置页标签 ── */
QLabel#settingLabel { color: #9b9788; font-size: 13px; font-family: 宋体; }

/* ── 滚动条 ── */
QScrollBar:vertical {
    background: #0d0d0b; width: 10px; border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #5a4f3e; border-radius: 5px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #ca8a04; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
"""

# ═══════════════════════════════════
#  浅色主题 QSS
# ═══════════════════════════════════
LIGHT_QSS = """
QMainWindow, QWidget {
    background-color: #fefcf4; color: #1c1915;
    font-family: 宋体, SimSun, serif; font-size: 13px;
}

QPushButton#NavBtn {
    background: #faf7ed; color: #7a7568; border: 1px solid #e8e2d0;
    border-radius: 10px; padding: 8px 24px; font-size: 14px; font-weight: bold;
    min-width: 80px; font-family: 宋体;
}
QPushButton#NavBtn:hover { background: #f0ead8; color: #b07d02; border-color: #b07d02; }
QPushButton#NavBtn:checked, QPushButton#NavBtn[active="true"] {
    background: #b07d02; color: #ffffff; border-color: #b07d02;
}

QPushButton#primaryBtn, QPushButton#warnBtn {
    background: #b07d02; color: #ffffff; border: none;
    border-radius: 10px; padding: 10px 24px; font-size: 14px; font-weight: bold;
    font-family: 宋体;
}
QPushButton#primaryBtn:hover, QPushButton#warnBtn:hover { background: #c89008; }
QPushButton#primaryBtn:disabled, QPushButton#warnBtn:disabled {
    background: #e8e2d0; color: #b0a998;
}
QPushButton#successBtn {
    background: #0f766e; color: #ffffff; border: none;
    border-radius: 10px; padding: 10px 24px; font-size: 14px; font-weight: bold;
    font-family: 宋体;
}
QPushButton#successBtn:hover { background: #12887e; }
QPushButton#successBtn:disabled { background: #d0e8e0; color: #b0a998; }

QPushButton#outlineBtn {
    background: transparent; color: #b07d02; border: 1px solid #b07d02;
    border-radius: 10px; padding: 8px 20px; font-size: 12px; font-family: 宋体;
}
QPushButton#outlineBtn:hover { background: rgba(176,125,2,0.08); }

QPushButton#dangerBtn {
    background: #c44a4a; color: #ffffff; border: none;
    border-radius: 10px; padding: 8px 20px; font-size: 12px; font-family: 宋体;
}
QPushButton#dangerBtn:hover { background: #d44a4a; }
QPushButton#dangerOutBtn {
    background: transparent; color: #c44a4a; border: 1px solid #c44a4a;
    border-radius: 10px; padding: 8px 20px; font-size: 12px; font-family: 宋体;
}
QPushButton#dangerOutBtn:hover { background: rgba(196,74,74,0.08); }
QPushButton#dangerOutBtn:disabled { color: #b0a998; border-color: #e8e2d0; }

QPushButton#themeDark, QPushButton#themeLight {
    background: #faf7ed; color: #7a7568; border: 1px solid #e8e2d0;
    border-radius: 10px; padding: 6px 16px; font-size: 12px; font-family: 宋体;
}
QPushButton#themeDark:checked, QPushButton#themeLight:checked {
    background: #b07d02; color: #ffffff; border-color: #b07d02;
}

QFrame#card { background: #faf7ed; border: 1px solid #e8e2d0; border-radius: 12px; }

QLabel#cardTitle { color: #1c1915; font-size: 14px; font-weight: bold; font-family: 宋体; }
QLabel#cardSubTitle { color: #7a7568; font-size: 12px; font-weight: bold; font-family: 宋体; }
QLabel#statusLabel { color: #7a7568; font-size: 12px; font-family: 宋体; }
QLabel#detailTitle { color: #1c1915; font-size: 14px; font-weight: bold; font-family: 宋体; }
QLabel#hintLabel { color: #7a7568; font-size: 12px; font-family: 宋体; }

QTextEdit, QPlainTextEdit {
    background: #fefcf4; color: #1c1915; border: 1px solid #e8e2d0;
    border-radius: 8px; padding: 12px; font-size: 14px; font-family: 宋体;
}
QTextEdit:focus, QPlainTextEdit:focus { border-color: #b07d02; }
QLineEdit {
    background: #fefcf4; color: #1c1915; border: 1px solid #e8e2d0;
    border-radius: 8px; padding: 10px; font-size: 13px; font-family: 宋体;
}
QLineEdit:focus { border-color: #b07d02; }

QComboBox {
    background: #fefcf4; color: #1c1915; border: 1px solid #e8e2d0;
    border-radius: 8px; padding: 8px; font-size: 13px; font-family: 宋体;
}
QComboBox:hover { border-color: #b07d02; }
QComboBox::drop-down { border: none; border-radius: 8px; subcontrol-origin: padding; subcontrol-position: top right; width: 24px; }
QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 7px solid #7a7568; margin-right: 8px; }
QComboBox QAbstractItemView {
    background: #faf7ed; color: #1c1915;
    selection-background-color: #b07d02; selection-color: #ffffff;
}

QTableWidget {
    background: #fefcf4; color: #1c1915; border: 1px solid #e8e2d0;
    border-radius: 8px; gridline-color: #e8e2d0; font-family: 宋体;
}
QTableWidget::item { padding: 8px 12px; }
QTableWidget::item:selected { background: #b07d02; color: #ffffff; }
QHeaderView::section {
    background: #faf7ed; color: #7a7568; padding: 8px;
    border: none; border-bottom: 1px solid #e8e2d0; font-weight: bold; font-family: 宋体;
}

QLabel { background: transparent; border: none; }
QLabel#settingLabel { color: #7a7568; font-size: 13px; font-family: 宋体; }

QScrollBar:vertical {
    background: #ede8d8; width: 10px; border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #b8b098; border-radius: 5px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #b07d02; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
"""


IS_DARK_THEME = True

def apply_app_theme(theme_name: str):
    """全局应用深/浅 QSS"""
    global IS_DARK_THEME
    is_light = theme_name in ("litera", "minty", "flatly", "cosmo",
                               "lumen", "pulse", "sandstone", "united",
                               "yeti", "morph", "journal", "simplex", "cerculean")
    IS_DARK_THEME = not is_light
    qss = LIGHT_QSS if is_light else DARK_QSS
    for widget in QApplication.topLevelWidgets():
        widget.setStyleSheet(qss)
        widget.style().unpolish(widget)
        widget.style().polish(widget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        settings = load_settings()
        self._theme = settings.theme if hasattr(settings, 'theme') else "darkly"

        self.setWindowTitle("易经占卜")
        self.resize(980, 760)
        self.setMinimumSize(740, 560)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 16)
        root.setSpacing(12)

        # ── 导航栏 ──
        nav = QHBoxLayout()
        nav.setSpacing(8)
        nav.addStretch()
        self._nav_btns = {}
        tabs = [("divination", "问  卦"), ("history", "历  史"), ("settings", "设  置")]
        for key, label in tabs:
            btn = QPushButton(label)
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._switch(k))
            nav.addWidget(btn)
            self._nav_btns[key] = btn
        nav.addStretch()
        root.addLayout(nav)

        # ── 页面栈 ──
        self.stack = QStackedWidget()
        self.divination_page = DivinationPage()
        self.history_page = HistoryPage()
        self.settings_page = SettingsPage()
        self.settings_page.theme_changed.connect(self._on_theme_changed)

        self.stack.addWidget(self.divination_page)
        self.stack.addWidget(self.history_page)
        self.stack.addWidget(self.settings_page)
        root.addWidget(self.stack, 1)

        self._switch("divination")
        apply_app_theme(self._theme)

    def _switch(self, key: str):
        pages = {"divination": 0, "history": 1, "settings": 2}
        self.stack.setCurrentIndex(pages.get(key, 0))
        for k, btn in self._nav_btns.items():
            btn.setChecked(k == key)
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        if key == "history":
            self.history_page.refresh_list()
        elif key == "settings":
            self.settings_page.load_settings()

    def _on_theme_changed(self, theme: str):
        self._theme = theme
        apply_app_theme(theme)
        self.divination_page.refresh_theme()
        s = load_settings()
        s.theme = theme
        save_settings(s)
