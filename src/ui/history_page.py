"""历史记录页面 —— 全局 QSS 统一样式"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QTextEdit, QHeaderView, QMessageBox, QFrame,
)
from PySide6.QtCore import Qt

from storage.history_db import (
    get_all_readings, search_readings, get_reading_by_id,
    delete_reading, clear_all_readings, get_reading_count,
)


class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._page_size = 20
        self._current_page = 0
        self._current_id = None
        self._setup_ui()
        self.refresh_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 搜索栏
        search_row = QHBoxLayout()
        search_label = QLabel("搜索：")
        search_label.setObjectName("settingLabel")
        search_row.addWidget(search_label)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键词搜索...")
        self.search_edit.returnPressed.connect(self._search)
        search_row.addWidget(self.search_edit, 1)

        search_btn = QPushButton("搜索")
        search_btn.setObjectName("outlineBtn")
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.clicked.connect(self._search)
        search_row.addWidget(search_btn)

        show_all_btn = QPushButton("显示全部")
        show_all_btn.setObjectName("outlineBtn")
        show_all_btn.setCursor(Qt.PointingHandCursor)
        show_all_btn.clicked.connect(self._show_all)
        search_row.addWidget(show_all_btn)
        layout.addLayout(search_row)

        # 表格卡片
        card = QFrame()
        card.setObjectName("card")
        tc = QVBoxLayout(card)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["日期", "问题", "本卦", "变卦"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_select)
        tc.addWidget(self.table, 1)

        # 分页
        page_row = QHBoxLayout()
        self.prev_btn = QPushButton("← 上一页")
        self.prev_btn.setObjectName("outlineBtn")
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(self._prev)
        page_row.addWidget(self.prev_btn)

        self.page_label = QLabel("第 0/0 页")
        self.page_label.setObjectName("statusLabel")
        self.page_label.setAlignment(Qt.AlignCenter)
        page_row.addWidget(self.page_label, 1)

        self.next_btn = QPushButton("下一页 →")
        self.next_btn.setObjectName("outlineBtn")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self._next)
        page_row.addWidget(self.next_btn)
        tc.addLayout(page_row)
        layout.addWidget(card, 1)

        # 详情卡片
        detail_card = QFrame()
        detail_card.setObjectName("card")
        dc = QVBoxLayout(detail_card)
        detail_title = QLabel("记录详情")
        detail_title.setObjectName("detailTitle")
        dc.addWidget(detail_title)
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(200)
        dc.addWidget(self.detail_text)

        btn_row = QHBoxLayout()
        clear_all_btn = QPushButton("清空全部")
        clear_all_btn.setObjectName("dangerBtn")
        clear_all_btn.setCursor(Qt.PointingHandCursor)
        clear_all_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(clear_all_btn)
        btn_row.addStretch()

        self.del_btn = QPushButton("删除此记录")
        self.del_btn.setObjectName("dangerOutBtn")
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.setEnabled(False)
        self.del_btn.clicked.connect(self._delete)
        btn_row.addWidget(self.del_btn)
        dc.addLayout(btn_row)
        layout.addWidget(detail_card)

    def _search(self):
        self._current_page = 0
        self.refresh_list()

    def _show_all(self):
        self.search_edit.clear()
        self._current_page = 0
        self.refresh_list()

    def _prev(self):
        if self._current_page > 0:
            self._current_page -= 1
            self.refresh_list()

    def _next(self):
        self._current_page += 1
        self.refresh_list()

    def refresh_list(self):
        keyword = self.search_edit.text().strip()
        total = get_reading_count(keyword) if keyword else get_reading_count()
        total_pages = max(1, (total + self._page_size - 1) // self._page_size) if total > 0 else 0
        if total > 0 and self._current_page >= total_pages:
            self._current_page = total_pages - 1
        offset = self._current_page * self._page_size
        readings = search_readings(keyword, limit=self._page_size, offset=offset) if keyword else get_all_readings(limit=self._page_size, offset=offset)

        self.table.setRowCount(len(readings))
        for row, r in enumerate(readings):
            q = r.get("question", "")
            self.table.setItem(row, 0, QTableWidgetItem(r["created_at"]))
            self.table.setItem(row, 1, QTableWidgetItem(q[:30] + "..." if len(q) > 30 else q))
            self.table.setItem(row, 2, QTableWidgetItem(r["hexagram_name"]))
            self.table.setItem(row, 3, QTableWidgetItem(r.get("changed_hexagram_name", "") or "-"))

        cur = self._current_page + 1 if total > 0 else 0
        self.page_label.setText(f"第 {cur}/{total_pages} 页")
        self.prev_btn.setEnabled(self._current_page > 0)
        self.next_btn.setEnabled((self._current_page + 1) * self._page_size < total)

    def _on_select(self):
        row = self.table.currentRow()
        if row < 0:
            self._current_id = None
            self.del_btn.setEnabled(False)
            return
        keyword = self.search_edit.text().strip()
        offset = self._current_page * self._page_size
        readings = search_readings(keyword, limit=self._page_size, offset=offset) if keyword else get_all_readings(limit=self._page_size, offset=offset)
        if row < len(readings):
            self._current_id = readings[row]["id"]
            self.del_btn.setEnabled(True)
            self._show_detail(readings[row])

    def _show_detail(self, reading):
        labels = {6: "老阴", 7: "少阳", 8: "少阴", 9: "老阳"}
        d = f"问题：{reading['question']}\n时间：{reading['created_at']}\n"
        d += f"方法：{'三铜钱法' if reading['method'] == 'coins' else '随机数法'}\n"
        d += f"本卦：{reading['hexagram_name']}（第{reading['hexagram_number']}卦）\n"
        if reading.get("changed_hexagram_name"):
            d += f"变卦：{reading['changed_hexagram_name']}（第{reading['changed_hexagram_number']}卦）\n"
        lines = reading.get("lines", [])
        if lines:
            d += "六爻：" + " → ".join(f"{v}({labels.get(v, '?')})" for v in lines) + "\n"
        d += "\n" + "-" * 40 + "\n\n"
        d += f"AI 解读：\n{reading['ai_analysis']}\n" if reading.get("ai_analysis") else "（未进行 AI 解读）\n"
        self.detail_text.setPlainText(d)

    def _delete(self):
        if self._current_id is None:
            return
        if QMessageBox.question(self, "确认删除", "确定要删除这条占卜记录吗？",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            delete_reading(self._current_id)
            self._current_id = None
            self.del_btn.setEnabled(False)
            self.detail_text.clear()
            self.refresh_list()

    def _clear_all(self):
        if QMessageBox.question(self, "确认清空", "确定要删除全部历史记录吗？",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            count = clear_all_readings()
            self._current_id = None
            self.del_btn.setEnabled(False)
            self.detail_text.clear()
            self.refresh_list()
            QMessageBox.information(self, "完成", f"已清空 {count} 条记录。")
