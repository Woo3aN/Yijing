"""主窗口 —— 三个标签页容器"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .divination_page import DivinationPage
from .history_page import HistoryPage
from .settings_page import SettingsPage


class MainWindow:
    """主窗口，包含 Notebook 标签页"""

    def __init__(self, root: ttk.Window):
        self.root = root

        # 创建 Notebook（标签页容器）
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        # 初始化三个页面
        self.divination_page = DivinationPage(self.notebook)
        self.history_page = HistoryPage(self.notebook)
        self.settings_page = SettingsPage(self.notebook)

        # 添加到 Notebook
        self.notebook.add(self.divination_page.frame, text="  问卦  ")
        self.notebook.add(self.history_page.frame, text="  历史记录  ")
        self.notebook.add(self.settings_page.frame, text="  设置  ")

        # 切换标签页时的回调
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        """标签页切换时刷新相应页面"""
        current_tab = self.notebook.select()
        tab_text = self.notebook.tab(current_tab, "text")
        if "历史" in tab_text:
            self.history_page.refresh_list()
        elif "设置" in tab_text:
            self.settings_page.load_current_settings()
