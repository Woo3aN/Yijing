"""历史记录页面 —— 浏览、搜索、查看、删除占卜记录"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

from storage.history_db import (
    get_all_readings, search_readings, get_reading_by_id, delete_reading,
    clear_all_readings,
)


class HistoryPage:
    """历史记录标签页"""

    def __init__(self, parent: ttk.Notebook):
        self.frame = ttk.Frame(parent)

        # ---- 搜索栏 ----
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=X, padx=10, pady=(10, 5))

        ttk.Label(search_frame, text="搜索：").pack(side=LEFT)
        self.search_var = ttk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, width=30
        )
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.refresh_list())

        ttk.Button(
            search_frame, text="搜索",
            command=self.refresh_list,
            bootstyle="outline-secondary"
        ).pack(side=LEFT)

        ttk.Button(
            search_frame, text="显示全部",
            command=self._show_all,
            bootstyle="outline-secondary"
        ).pack(side=LEFT, padx=5)

        # ---- 历史列表（Treeview） ----
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=BOTH, expand=YES, padx=10, pady=5)

        columns = ("created_at", "question", "hexagram", "changed")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings",
            height=12, selectmode="browse"
        )
        self.tree.heading("created_at", text="日期")
        self.tree.heading("question", text="问题")
        self.tree.heading("hexagram", text="本卦")
        self.tree.heading("changed", text="变卦")

        self.tree.column("created_at", width=130, anchor=CENTER)
        self.tree.column("question", width=250)
        self.tree.column("hexagram", width=100, anchor=CENTER)
        self.tree.column("changed", width=100, anchor=CENTER)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ---- 详情面板 ----
        detail_frame = ttk.LabelFrame(self.frame, text="记录详情")
        detail_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(5, 10))

        self.detail_text = ttk.Text(
            detail_frame, height=10, wrap=WORD,
            font=("等线", 10)
        )
        self.detail_text.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        # ---- 操作按钮 ----
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=X, padx=10, pady=(0, 10))

        self.clear_all_btn = ttk.Button(
            btn_frame, text="清空全部",
            command=self._clear_all,
            bootstyle="danger",
        )
        self.clear_all_btn.pack(side=LEFT)

        self.delete_btn = ttk.Button(
            btn_frame, text="删除此记录",
            command=self._delete_selected,
            bootstyle="danger-outline",
            state=DISABLED
        )
        self.delete_btn.pack(side=RIGHT)

        self._current_id: int | None = None

        # 初始加载
        self.refresh_list()

    def refresh_list(self):
        """刷新历史列表"""
        # 清空现有列表
        for item in self.tree.get_children():
            self.tree.delete(item)

        keyword = self.search_var.get().strip()
        if keyword:
            readings = search_readings(keyword)
        else:
            readings = get_all_readings()

        for r in readings:
            question_display = r["question"][:30] + "..." if len(r.get("question", "")) > 30 else r.get("question", "")
            changed_display = r.get("changed_hexagram_name", "") or "-"
            self.tree.insert("", END, iid=r["id"], values=(
                r["created_at"],
                question_display,
                r["hexagram_name"],
                changed_display,
            ))

    def _show_all(self):
        """显示全部记录"""
        self.search_var.set("")
        self.refresh_list()

    def _on_select(self, event):
        """选中历史记录时的回调"""
        selection = self.tree.selection()
        if not selection:
            self._current_id = None
            self.delete_btn.configure(state=DISABLED)
            return

        item_id = int(selection[0])
        self._current_id = item_id
        self.delete_btn.configure(state=NORMAL)

        reading = get_reading_by_id(item_id)
        if not reading:
            return

        # 构建详情文本
        lines = reading.get("lines", [])
        line_labels = {6: "老阴", 7: "少阳", 8: "少阴", 9: "老阳"}

        detail = f"问题：{reading['question']}\n"
        detail += f"时间：{reading['created_at']}\n"
        detail += f"方法：{'三铜钱法' if reading['method'] == 'coins' else '随机数法'}\n"
        detail += f"本卦：{reading['hexagram_name']}（第{reading['hexagram_number']}卦）\n"

        if reading.get("changed_hexagram_name"):
            detail += f"变卦：{reading['changed_hexagram_name']}（第{reading['changed_hexagram_number']}卦）\n"

        if lines:
            line_strs = []
            for v in lines:
                lbl = line_labels.get(v, "?")
                line_strs.append(f"{v}({lbl})")
            detail += "六爻：" + " → ".join(line_strs) + "\n"

        detail += "\n" + "-" * 40 + "\n\n"

        if reading.get("ai_analysis"):
            detail += f"AI 解读：\n{reading['ai_analysis']}\n"
        else:
            detail += "（未进行 AI 解读）\n"

        self.detail_text.delete("1.0", END)
        self.detail_text.insert("1.0", detail)

    def _delete_selected(self):
        """删除选中的记录"""
        if self._current_id is None:
            return

        if messagebox.askyesno("确认删除", "确定要删除这条占卜记录吗？此操作不可撤销。"):
            delete_reading(self._current_id)
            self._current_id = None
            self.delete_btn.configure(state=DISABLED)
            self.detail_text.delete("1.0", END)
            self.refresh_list()

    def _clear_all(self):
        """清空全部历史记录"""
        if messagebox.askyesno("确认清空", "确定要删除全部历史记录吗？此操作不可撤销。"):
            count = clear_all_readings()
            self._current_id = None
            self.delete_btn.configure(state=DISABLED)
            self.detail_text.delete("1.0", END)
            self.refresh_list()
            messagebox.showinfo("完成", f"已清空 {count} 条记录。")
