"""问卦页面 —— 单 Text 原生滚动 + 富文本标签排版"""

import random
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from core.divination import (
    coin_method, random_method, perform_divination,
    line_value_to_chinese, is_changing_line,
    OLD_YIN, YOUNG_YANG, YOUNG_YIN, OLD_YANG,
)
from core.text_loader import get_hexagram
from storage.history_db import save_reading
from storage.app_settings import has_api_key

COIN_GLYPHS = {0: "◯", 1: "●"}
POS_NAMES   = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
CHANGE_DESC = {6: "老阴 → 少阳", 9: "老阳 → 少阴"}


class DivinationPage:
    """问卦标签页"""

    def __init__(self, parent: ttk.Notebook):
        self.frame = ttk.Frame(parent)
        self._current_result: dict | None = None
        self._primary_data: dict | None = None
        self._changed_data: dict | None = None
        self._ai_stream_id: str | None = None
        self._build_ui()
        self._setup_tags()

    # ═══════════════════════════════════
    #  Text 富文本标签
    # ═══════════════════════════════════

    def _setup_tags(self):
        """配置 Text 组件的富文本样式标签 —— 媲美卡片式排版"""
        r = self.result_text

        # 标题（加大间距，层次分明）
        r.tag_configure("h1", font=("楷体", 17, "bold"), foreground="#ffffff")
        r.tag_configure("h2", font=("楷体", 14, "bold"), foreground="#dddddd")
        r.tag_configure("h3", font=("楷体", 12, "bold"), foreground="#cccccc")

        # 正文
        r.tag_configure("body", font=("等线", 10), foreground="#cccccc")

        # 卦名（大字楷体）
        r.tag_configure("guaming", font=("楷体", 19, "bold"), foreground="#ffffff")
        r.tag_configure("guafu", font=("Microsoft YaHei", 42), foreground="#ffffff")

        # 六爻线条
        r.tag_configure("line_default", font=("楷体", 13), foreground="#bbbbbb")
        r.tag_configure("line_changed", font=("楷体", 13), foreground="#f1c40f")

        # 高亮 — 楷体加粗白色（AI 小标题）
        r.tag_configure("highlight", font=("楷体", 11, "bold"), foreground="#ffffff")
        # 本卦/变卦 badge 颜色
        r.tag_configure("tag_primary", font=("楷体", 11, "bold"), foreground="#3498db")
        r.tag_configure("tag_change", font=("楷体", 11, "bold"), foreground="#e67e22")
        # 警告/变爻颜色
        r.tag_configure("warn", font=("等线", 10), foreground="#f39c12")
        # 灰色备注
        r.tag_configure("dim", font=("等线", 9), foreground="#888888")

        # 分隔线
        r.tag_configure("sep", font=("等线", 4), foreground="#444444")

        # 爻辞
        r.tag_configure("line_chg", font=("等线", 10, "bold"), foreground="#f39c12")
        r.tag_configure("line_normal", font=("等线", 10), foreground="#cccccc")

        # 居中占位提示
        r.tag_configure("placeholder", font=("楷体", 13), foreground="#666666",
                        justify="center")
        r.tag_configure("center", justify="center")

    # ═══════════════════════════════════
    #  UI 构建
    # ═══════════════════════════════════

    def _build_ui(self):
        """顶部固定 + 过程区 + 结果区（单 Text，富文本）"""

        # ── 顶部 ──
        top = ttk.Frame(self.frame)
        top.pack(fill=X, padx=16, pady=(16, 0))

        input_frame = ttk.LabelFrame(top, text=" 所问何事 ")
        input_frame.pack(fill=X)

        self.question_text = ttk.Text(
            input_frame, height=3, wrap=WORD, font=("等线", 11)
        )
        self.question_text.pack(fill=X, padx=10, pady=10)
        self._placeholder = "例如：我最近的事业运势如何？这次考试结果会怎样？"
        self.question_text.insert("1.0", self._placeholder)
        self.question_text.configure(foreground="#888888")
        self.question_text.bind("<FocusIn>", self._on_focus_in)
        self.question_text.bind("<FocusOut>", self._on_focus_out)

        btn_row = ttk.Frame(top)
        btn_row.pack(fill=X, pady=(10, 0))

        coin_col = ttk.Frame(btn_row)
        coin_col.pack(side=LEFT, padx=(0, 16), fill=X, expand=YES)
        self.coin_btn = ttk.Button(
            coin_col, text="☰  三 铜 钱 法",
            command=lambda: self._start_divination("coins"),
            bootstyle="primary",
        )
        self.coin_btn.pack(fill=X, ipady=6)
        ttk.Label(coin_col, text="逐爻摇卦 · 传统仪式",
                  font=("等线", 9), foreground="#999999").pack()

        rand_col = ttk.Frame(btn_row)
        rand_col.pack(side=LEFT, fill=X, expand=YES)
        self.random_btn = ttk.Button(
            rand_col, text="✦  随 机 数 法",
            command=lambda: self._start_divination("random"),
            bootstyle="success",
        )
        self.random_btn.pack(fill=X, ipady=6)
        ttk.Label(rand_col, text="一键生成 · 快速便捷",
                  font=("等线", 9), foreground="#999999").pack()

        # ── 过程区 ──
        self.process_frame = ttk.LabelFrame(self.frame, text=" 摇卦过程 ")
        self.process_text = ttk.Text(
            self.process_frame, height=9, wrap=WORD,
            font=("楷体", 11), state=DISABLED,
            spacing2=3,
        )
        self.process_text.pack(fill=X, padx=10, pady=10)

        # ── 结果区：单 Text，原生滚动 ──
        result_frame = ttk.LabelFrame(self.frame, text=" 卦象结果 ")
        result_frame.pack(fill=BOTH, expand=YES, padx=16, pady=10)

        self.result_text = ttk.Text(
            result_frame, wrap=WORD, font=("等线", 10),
            state=DISABLED, spacing2=1,
        )
        scrollbar = ttk.Scrollbar(result_frame, orient=VERTICAL,
                                  command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)

        self.result_text.pack(side=LEFT, fill=BOTH, expand=YES, padx=(8, 0), pady=8)
        scrollbar.pack(side=RIGHT, fill=Y, padx=(0, 4), pady=8)

        # 初始提示
        self._show_placeholder("点击上方按钮开始起卦")

    # ═══════════════════════════════════
    #  输入框交互
    # ═══════════════════════════════════

    def _on_focus_in(self, event):
        if self.question_text.get("1.0", "end-1c") == self._placeholder:
            self.question_text.delete("1.0", END)
            self.question_text.configure(foreground="#ffffff")

    def _on_focus_out(self, event):
        if not self.question_text.get("1.0", "end-1c").strip():
            self.question_text.insert("1.0", self._placeholder)
            self.question_text.configure(foreground="#888888")

    def _get_question(self) -> str:
        text = self.question_text.get("1.0", "end-1c").strip()
        return "" if text == self._placeholder else text

    def _show_placeholder(self, text: str):
        """显示占位提示"""
        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.insert("1.0", f"\n\n\n\n    ☯\n\n    {text}\n\n\n", ("placeholder",))
        self.result_text.configure(state=DISABLED)

    # ═══════════════════════════════════
    #  起卦
    # ═══════════════════════════════════

    def _start_divination(self, method: str):
        self.coin_btn.configure(state=DISABLED)
        self.random_btn.configure(state=DISABLED)
        self._cancel_ai_stream()

        self.process_frame.pack(fill=X, padx=16, pady=(0, 6),
                                before=self.result_text.master)
        self.process_text.configure(state=NORMAL)
        self.process_text.delete("1.0", END)
        self.process_text.insert(END, "起卦中……\n\n")

        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.configure(state=DISABLED)

        if method == "coins":
            self._do_coin_method()
        else:
            self._do_random_method()

    def _do_coin_method(self):
        lines = []

        def toss_line(i: int):
            if i >= 6:
                self._show_result(lines, "coins")
                return

            coins = [random.randint(0, 1) for _ in range(3)]
            heads = sum(coins)
            value = [OLD_YIN, YOUNG_YANG, YOUNG_YIN, OLD_YANG][heads]
            lines.append(value)

            label = line_value_to_chinese(value)
            coin_row = "  ".join(COIN_GLYPHS[c] for c in coins)
            is_chg = is_changing_line(value)

            # 格式化：爻位 │ 铜钱 │ 结果
            pos = f"  {POS_NAMES[i]:　<4s}"
            coins_display = f"  {coin_row}"
            result = f"→  {label}（{value}）"
            mark = "  ◈ 变爻" if is_chg else ""

            line = f"{pos}│{coins_display}  │  {result}{mark}\n"
            self.process_text.insert(END, line)
            self.process_text.see(END)
            self.frame.after(500, lambda: toss_line(i + 1))

        toss_line(0)

    def _do_random_method(self):
        lines = random.choices(
            [OLD_YIN, YOUNG_YANG, YOUNG_YIN, OLD_YANG],
            weights=[1, 3, 3, 1], k=6
        )
        for i, v in enumerate(lines):
            label = line_value_to_chinese(v)
            mark = "  ◈ 变爻" if is_changing_line(v) else ""
            self.process_text.insert(END,
                f"  {POS_NAMES[i]}   →   ({v})  {label}{mark}\n"
            )
        self._show_result(lines, "random")

    # ═══════════════════════════════════
    #  结果渲染（带富文本标签）
    # ═══════════════════════════════════

    def _show_result(self, lines: list[int], method: str):
        from core.divination import lines_to_binary, get_binary_lookup

        primary_bin, changed_bin, changing = lines_to_binary(lines)
        lookup = get_binary_lookup()
        primary_num = lookup[primary_bin]
        changed_num = lookup[changed_bin] if changed_bin else None

        self._primary_data = get_hexagram(primary_num)
        self._changed_data = get_hexagram(changed_num) if changed_num else None
        self._current_result = {
            "lines": lines, "primary_binary": primary_bin,
            "changed_binary": changed_bin, "changing_lines": changing,
            "primary_number": primary_num, "changed_number": changed_num,
        }

        r = self.result_text
        r.configure(state=NORMAL)
        r.delete("1.0", END)

        # ── 六爻线条图 ──
        self._ins(r, "\n", ("center",))
        for i in range(5, -1, -1):
            v = lines[i]
            is_chg = is_changing_line(v)
            is_yang = v in (YOUNG_YANG, OLD_YANG)
            bar = "━━━━━━━━━━━━━━━━━━" if is_yang else "━━━━━━━━　　━━━━━━━━"
            # 变爻在行首用 ◆ 标记，后缀统一为 "   初爻"（4空格+爻名）
            prefix = " ◆" if is_chg else "   "
            suffix = f"    {POS_NAMES[i]}"
            style = "line_changed" if is_chg else "line_default"
            self._ins(r, prefix + bar + suffix + "\n", (style, "center"))

        self._ins_sep(r)

        # ── 本卦 ──
        self._ins_hexagram(r, self._primary_data, "本  卦", "tag_primary",
                           changing_lines=changing)

        # ── 变卦 ──
        if self._changed_data:
            self._ins_sep(r)
            self._ins_hexagram(r, self._changed_data, "变  卦", "tag_change")

        # ── 变爻详情 ──
        if changing:
            self._ins_sep(r)
            self._ins(r, "变爻详情\n", ("h2",))
            for pos in changing:
                ld = self._primary_data["lines"][pos - 1]
                desc = CHANGE_DESC.get(lines[pos - 1], "")
                self._ins(r, f"  第{pos}爻  {ld['label']}：{ld['text']}　", ("body",))
                self._ins(r, f"← {desc}\n", ("warn",))
                self._ins(r, f"      {ld['xiang']}\n\n", ("dim",))

        # ── 朱熹断卦规则 ──
        self._ins_sep(r)
        self._ins_zhuxi(r, lines)

        # ── AI 区域占位 ──
        self._ins_sep(r)
        self._ins(r, "AI 解读\n", ("h2",))
        self._ins(r, "（配置 API 密钥后点击 AI 解卦按钮）\n", ("dim",))
        # 在占位文本之后设一个 mark，AI 内容都从这里开始
        r.mark_set("ai_content_start", END + "-1c")
        r.mark_gravity("ai_content_start", "left")

        r.configure(state=DISABLED)
        r.see("1.0")  # 回到顶部

        self.process_frame.pack_forget()
        self._show_ai_button()

        save_reading(
            question=self._get_question(), method=method, lines=lines,
            hexagram_number=primary_num, hexagram_name=self._primary_data["name"],
            changed_hexagram_number=changed_num,
            changed_hexagram_name=self._changed_data["name"] if self._changed_data else None,
        )

        self.coin_btn.configure(state=NORMAL)
        self.random_btn.configure(state=NORMAL)

    # ── 插入辅助函数 ──

    def _ins(self, r, text: str, tags=()):
        r.insert(END, text, tags)

    def _ins_sep(self, r):
        self._ins(r, "─" * 50 + "\n", ("sep",))

    def _ins_hexagram(self, r, data: dict, badge: str, badge_tag: str,
                      changing_lines=None):
        """插入卦象卡片"""
        self._ins(r, f" {badge}  ", (badge_tag,))
        self._ins(r, f"{data['symbol']}  ", ("guafu",))
        self._ins(r, f"{data['name']}\n", ("guaming",))
        self._ins(r, f"第 {data['number']} 卦　·　{data['pinyin']}\n", ("dim",))
        self._ins(r, f"上{data['upper_trigram']}　下{data['lower_trigram']}\n\n", ("dim",))

        self._ins(r, "卦　辞　", ("h3",))
        self._ins(r, f"{data['judgment']}\n\n", ("body",))

        self._ins(r, "彖　传　", ("h3",))
        self._ins(r, f"{data['tuan_zhuan']}\n\n", ("body",))

        self._ins(r, "大象传　", ("h3",))
        self._ins(r, f"{data['xiang_zhuan']}\n\n", ("body",))

        self._ins(r, "爻　辞\n", ("h3",))
        for line in data["lines"]:
            is_chg = changing_lines and line["position"] in changing_lines
            tag = "line_chg" if is_chg else "line_normal"
            prefix = "◆" if is_chg else "·"
            self._ins(r, f"  {prefix} {line['label']}：{line['text']}\n", (tag,))

    def _ins_zhuxi(self, r, lines: list[int]):
        """插入朱熹断卦规则"""
        from core.divination import get_interpretation_rule, get_focus_text

        n = sum(1 for v in lines if v in (OLD_YIN, OLD_YANG))
        rule = get_interpretation_rule(n)
        focus = get_focus_text(lines, self._primary_data, self._changed_data)

        self._ins(r, "断卦规则\n", ("h2",))
        self._ins(r, f"朱熹《周易启蒙》· {rule['rule']}\n", ("warn",))
        self._ins(r, f"{rule['description']}\n\n", ("body",))

        self._ins(r, f"▼ 重点看：{focus['focus_title']}\n", ("highlight",))
        self._ins(r, "\n", ())
        for line in focus["focus_content"].split("\n"):
            self._ins(r, f"  {line}\n", ("body",))

    # ═══════════════════════════════════
    #  AI
    # ═══════════════════════════════════

    def _show_ai_button(self):
        if hasattr(self, '_ai_btn_frame'):
            self._ai_btn_frame.destroy()

        self._ai_btn_frame = ttk.Frame(self.result_text.master)
        self._ai_btn_frame.pack(anchor=E, padx=10, pady=(6, 0),
                                before=self.result_text)

        self.ai_btn = ttk.Button(
            self._ai_btn_frame, text="🤖  AI 解卦",
            command=self._request_ai_analysis,
            bootstyle="warning", state=DISABLED,
        )
        self.ai_btn.pack(side=LEFT, padx=(0, 10))

        self.ai_status = ttk.Label(self._ai_btn_frame, text="", font=("等线", 9))
        self.ai_status.pack(side=LEFT)

        self._update_ai_button_state()

    def _update_ai_button_state(self):
        if has_api_key():
            self.ai_btn.configure(state=NORMAL)
            self.ai_status.configure(text="已配置 API，可解读", foreground="#999999")
        else:
            self.ai_btn.configure(state=DISABLED)
            self.ai_status.configure(
                text="未配置 API 密钥", foreground="#999999")

    def _apply_ai_highlight(self):
        """扫描 AI 结果，自动给疑似小标题加粗"""
        import re
        r = self.result_text
        r.configure(state=NORMAL)
        # 从 ai_stream mark 开始到末尾
        start = r.index("ai_stream")
        end = r.index(END + "-1c")
        text = r.get(start, end)
        lines = text.split("\n")
        pos = start
        for line in lines:
            stripped = line.strip()
            is_heading = False
            # 模式匹配：小标题特征
            if len(stripped) <= 30 and len(stripped) >= 4:
                # 以数字+分隔符开头
                if re.match(r'^[一二三四五六七八九十\d]+[、.．）\)]\s*', stripped):
                    is_heading = True
                # 以汉字数字结尾带冒号
                elif re.match(r'^.{2,28}[：:]$', stripped):
                    is_heading = True
                # 全行都是重要标记
                elif '启示' in stripped or '建议' in stripped or '总结' in stripped or '分析' in stripped:
                    if len(stripped) <= 15:
                        is_heading = True
            if is_heading:
                line_start = f"{pos} +{len(line) - len(stripped)}c"
                line_end = f"{line_start} +{len(stripped)}c"
                r.tag_add("highlight", line_start, line_end)
            # 移动到下一行
            pos = r.index(f"{pos} +1 line")
        r.configure(state=DISABLED)

    def _save_ai_to_history(self, ai_text: str):
        """将 AI 解读结果更新到最近一条历史记录"""
        try:
            from storage.history_db import get_all_readings
            records = get_all_readings(limit=1, offset=0)
            if records:
                rid = records[0]["id"]
                from storage.history_db import update_ai_analysis
                update_ai_analysis(rid, ai_text)
        except Exception:
            pass  # 静默处理，不影响主流程

    def _cancel_ai_stream(self):
        if self._ai_stream_id:
            self.frame.after_cancel(self._ai_stream_id)
            self._ai_stream_id = None

    def _request_ai_analysis(self):
        if not self._current_result or not self._primary_data:
            return
        if not has_api_key():
            self.ai_status.configure(text="请先在「设置」中配置 API 密钥",
                                     foreground="#e74c3c")
            return

        self._cancel_ai_stream()

        lines_detail = "\n".join(
            f"{l['label']}：{l['text']}" for l in self._primary_data["lines"]
        )
        changing_lines = self._current_result.get("changing_lines", [])
        changing_info = ""
        if changing_lines and self._primary_data:
            parts = [f"第{p}爻 {self._primary_data['lines'][p-1]['label']}：{self._primary_data['lines'][p-1]['text']}"
                     for p in changing_lines]
            changing_info = "\n".join(parts)

        from core.divination import get_focus_text
        focus = get_focus_text(
            self._current_result["lines"], self._primary_data, self._changed_data
        )
        zhuxi_rule = f"{focus['rule']}：{focus['description']}"
        zhuxi_focus = f"【{focus['focus_title']}】\n{focus['focus_content']}"

        # 在结果末尾追加 AI 区域（用 mark 精确定位，杜绝位置错误）
        r = self.result_text
        r.configure(state=NORMAL)
        # 删除 ai_content_start mark 之后的一切旧内容
        r.delete("ai_content_start", END)
        # 插入加载提示，并在其后设 stream mark
        r.insert(END, "\nAI 解读中...\n")
        r.mark_set("ai_stream", END + "-1c")
        r.mark_gravity("ai_stream", "left")
        r.configure(state=DISABLED)

        self.ai_btn.configure(state=DISABLED, text="解读中...")
        self.ai_status.configure(text="正在请求 AI 解读...", foreground="#999999")

        collected = [""]

        def clean_md(text: str) -> str:
            import re
            text = re.sub(r'#{2,}\s*', '', text)
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            text = re.sub(r'\*(.+?)\*', r'\1', text)
            text = re.sub(r'`(.+?)`', r'\1', text)
            return text

        def run():
            try:
                from ai.llm_client import analyze
                result = analyze(
                    question=self._get_question(),
                    hexagram_name=self._primary_data["name"],
                    hexagram_symbol=self._primary_data["symbol"],
                    judgment=self._primary_data["judgment"],
                    tuan_zhuan=self._primary_data["tuan_zhuan"],
                    xiang_zhuan=self._primary_data["xiang_zhuan"],
                    lines=self._current_result["lines"],
                    lines_detail=lines_detail,
                    changed_name=self._changed_data["name"] if self._changed_data else None,
                    changed_symbol=self._changed_data["symbol"] if self._changed_data else None,
                    changing_lines=changing_lines,
                    changing_info=changing_info,
                    zhuxi_rule=zhuxi_rule,
                    zhuxi_focus=zhuxi_focus,
                )
                text = clean_md(result)

                self.frame.after(0, lambda: r.configure(state=NORMAL))
                self.frame.after(0, lambda: r.delete("ai_stream", END))
                self.frame.after(0, lambda: r.insert(END, text + "\n"))
                self.frame.after(0, lambda: self._apply_ai_highlight())
                self.frame.after(0, lambda: r.configure(state=DISABLED))
                # 保存 AI 结果到历史记录
                self.frame.after(0, lambda: self._save_ai_to_history(text))
                self.frame.after(0, lambda: self.ai_status.configure(
                    text="✓ 解读完成", foreground="#2ecc71"))
                self.frame.after(0, lambda: self.ai_btn.configure(
                    state=NORMAL, text="🤖  AI 解卦"))
            except Exception as e:
                self.frame.after(0, lambda: r.configure(state=NORMAL))
                self.frame.after(0, lambda: r.delete("ai_stream", END))
                self.frame.after(0, lambda: r.insert(END, f"请求失败：{e}\n"))
                self.frame.after(0, lambda: r.configure(state=DISABLED))
                self.frame.after(0, lambda: self.ai_status.configure(
                    text=f"失败：{e}", foreground="#e74c3c"))
                self.frame.after(0, lambda: self.ai_btn.configure(
                    state=NORMAL, text="🤖  AI 解卦"))

        threading.Thread(target=run, daemon=True).start()
