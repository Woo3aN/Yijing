"""问卦页面 —— PySide6 版本"""

import random
import threading
import re

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QScrollArea, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from core.divination import (
    coin_method, random_method, perform_divination,
    line_value_to_chinese, is_changing_line,
    OLD_YIN, YOUNG_YANG, YOUNG_YIN, OLD_YANG,
    lines_to_binary, get_binary_lookup, get_interpretation_rule, get_focus_text,
)
from core.text_loader import get_hexagram
from storage.history_db import save_reading
from storage.app_settings import has_api_key

COIN_GLYPHS = {0: "◯", 1: "●"}
POS_NAMES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
CHANGE_DESC = {6: "老阴 → 少阳", 9: "老阳 → 少阴"}


class DivinationPage(QWidget):
    ai_done = Signal(str)
    ai_error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_result = None
        self._primary_data = None
        self._changed_data = None
        self._lines = []
        self._ai_text = None  # 保存 AI 解读，主题切换时恢复
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ── 输入区 ──
        card1 = QFrame()
        card1.setObjectName("card")
        c1 = QVBoxLayout(card1)
        title1 = QLabel("●  所 问 何 事")
        title1.setObjectName("cardTitle")
        c1.addWidget(title1)

        self.question_edit = QTextEdit()
        self.question_edit.setPlaceholderText("例如：我最近的事业运势如何？这次考试结果会怎样？")
        self.question_edit.setMaximumHeight(72)
        c1.addWidget(self.question_edit)
        layout.addWidget(card1)

        # ── 按钮区 ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.coin_btn = QPushButton("☰  三 铜 钱 法")
        self.coin_btn.setObjectName("primaryBtn")
        self.coin_btn.setCursor(Qt.PointingHandCursor)
        self.coin_btn.clicked.connect(lambda: self._start("coins"))
        btn_row.addWidget(self.coin_btn, 1)

        self.random_btn = QPushButton("✦  随 机 数 法")
        self.random_btn.setObjectName("successBtn")
        self.random_btn.setCursor(Qt.PointingHandCursor)
        self.random_btn.clicked.connect(lambda: self._start("random"))
        btn_row.addWidget(self.random_btn, 1)

        layout.addLayout(btn_row)

        # ── 过程区 ──
        self.process_card = QFrame()
        self.process_card.setObjectName("card")
        pc = QVBoxLayout(self.process_card)
        self.process_label = QLabel("  ·  摇 卦 过 程  ·  ")
        self.process_label.setObjectName("cardSubTitle")
        pc.addWidget(self.process_label)
        self.process_text = QTextEdit()
        self.process_text.setReadOnly(True)
        self.process_text.setMaximumHeight(180)
        pc.addWidget(self.process_text)
        self.process_card.hide()
        layout.addWidget(self.process_card)

        # ── 结果区 ──
        result_card = QFrame()
        result_card.setObjectName("card")
        rc = QVBoxLayout(result_card)
        rlbl = QLabel("  ·  卦 象 结 果  ·  ")
        rlbl.setObjectName("cardSubTitle")
        rc.addWidget(rlbl)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        rc.addWidget(self.result_text, 1)

        # AI 按钮行
        ai_row = QHBoxLayout()
        self.copy_btn = QPushButton("📋 复制结果")
        self.copy_btn.setObjectName("outlineBtn")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_result)
        ai_row.addWidget(self.copy_btn)

        self.export_btn = QPushButton("💾 导出文本")
        self.export_btn.setObjectName("outlineBtn")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.clicked.connect(self._export_result)
        ai_row.addWidget(self.export_btn)

        ai_row.addStretch()
        self.ai_btn = QPushButton("🤖  AI 解卦")
        self.ai_btn.setObjectName("warnBtn")
        self.ai_btn.setCursor(Qt.PointingHandCursor)
        self.ai_btn.clicked.connect(self._request_ai)
        ai_row.addWidget(self.ai_btn)
        rc.addLayout(ai_row)

        self.ai_status = QLabel()
        self.ai_status.setObjectName("statusLabel")
        rc.addWidget(self.ai_status)

        self._update_ai_btn()

        layout.addWidget(result_card, 1)

        self._place_holder_text = "点击上方按钮开始起卦"
        self._show_placeholder()

        self.ai_done.connect(self._on_ai_done)
        self.ai_error.connect(self._on_ai_error)

    def refresh_theme(self):
        """主题切换后重渲染，保留 AI 内容"""
        if self._current_result and self._primary_data:
            s = self.result_text.verticalScrollBar().value()
            self._render_result()
            if self._ai_text:
                self._append_ai_html(self._ai_text)
            self.result_text.verticalScrollBar().setValue(s)

    def _append_ai_html(self, text: str):
        """在结果末尾追加 AI 解读 HTML"""
        current = self.result_text.toHtml()
        ai_block = (
            '<hr style="border-color:#2e2c24; margin:16px 0;">'
            '<div>'
            f'{self._format_ai(text)}'
            '</div>'
        )
        self.result_text.setHtml(current + ai_block)

    def _update_ai_btn(self):
        if has_api_key():
            self.ai_btn.setEnabled(True)
            self.ai_status.setText("已配置 API，可解读")
        else:
            self.ai_btn.setEnabled(False)
            self.ai_status.setText("未配置 API 密钥")
        self.ai_status.setObjectName("statusLabel")

    def _show_placeholder(self):
        self.result_text.setHtml(
            '<div style="text-align:center; padding:60px 0; color:#5e5a4e; font-size:18px; font-family:楷体,KaiTi,serif;">'
            f'☯<br><br>{self._place_holder_text}</div>'
        )

    # ═══ 起卦 ═══

    def _start(self, method: str):
        self.coin_btn.setEnabled(False)
        self.random_btn.setEnabled(False)
        QTimer.singleShot(8000, self._re_enable_buttons)  # 8秒兜底
        self._lines = []
        self.process_text.clear()

        if method == "coins":
            self.process_card.show()
            self.process_text.append("起卦中……\n")
            self._toss_line(0)
        else:
            lines = random.choices([OLD_YIN, YOUNG_YANG, YOUNG_YIN, OLD_YANG],
                                   weights=[1, 3, 3, 1], k=6)
            self._lines = lines
            self._show_result("random")

    def _re_enable_buttons(self):
        """恢复起卦按钮（安全兜底）"""
        self.coin_btn.setEnabled(True)
        self.random_btn.setEnabled(True)

    def _toss_line(self, i: int):
        if i >= 6:
            self._show_result("coins")
            return
        coins = [random.randint(0, 1) for _ in range(3)]
        heads = sum(coins)
        value = [OLD_YIN, YOUNG_YANG, YOUNG_YIN, OLD_YANG][heads]
        self._lines.append(value)
        label = line_value_to_chinese(value)
        coin_row = "  ".join(COIN_GLYPHS[c] for c in coins)
        is_chg = is_changing_line(value)
        mark = "  ◈ 变爻" if is_chg else ""
        self.process_text.append(
            f"  {POS_NAMES[i]}　{coin_row}　→  {label}（{value}）{mark}"
        )
        QTimer.singleShot(400, lambda: self._toss_line(i + 1))

    # ═══ 结果 ═══

    def _show_result(self, method: str):
        try:
            from core.divination import lines_to_binary, get_binary_lookup
            primary_bin, changed_bin, changing = lines_to_binary(self._lines)
            lookup = get_binary_lookup()
            primary_num = lookup[primary_bin]
            changed_num = lookup[changed_bin] if changed_bin else None

            self._primary_data = get_hexagram(primary_num)
            self._changed_data = get_hexagram(changed_num) if changed_num else None
            self._current_result = {
                "lines": self._lines, "primary_binary": primary_bin,
                "changed_binary": changed_bin, "changing_lines": changing,
                "primary_number": primary_num, "changed_number": changed_num,
            }
            self._render_result()

            self.process_card.hide()
            save_reading(
                question=self._get_question(), method=method, lines=self._lines,
                hexagram_number=primary_num, hexagram_name=self._primary_data["name"],
                changed_hexagram_number=changed_num,
                changed_hexagram_name=self._changed_data["name"] if self._changed_data else None,
            )
        except Exception as e:
            self.result_text.setPlainText(f"渲染出错：{e}")
        finally:
            self._update_ai_btn()
            self.coin_btn.setEnabled(True)
            self.random_btn.setEnabled(True)

    def _is_dark(self):
        """判断当前是否为深色主题"""
        from ui.main_window import IS_DARK_THEME
        return IS_DARK_THEME

    def _tc(self, dark_hex, light_hex=None):
        """返回适配当前主题的颜色"""
        if self._is_dark():
            return dark_hex
        return light_hex or dark_hex  # 如果没指定浅色，适当调暗

    def _render_result(self):
        """渲染卦象结果为 HTML"""
        changing = self._current_result.get("changing_lines", [])
        text = self._tc("#f0ece0", "#1c1915")  # 正文色
        dim = self._tc("#5e5a4e", "#3a3630")
        secondary = self._tc("#9b9788", "#2e2a25")
        parts = []

        # 六爻图
        parts.append('<div style="text-align:center; font-family:楷体,KaiTi,serif; font-size:17px; line-height:2.2;">')
        for i in range(5, -1, -1):
            v = self._lines[i]
            is_chg = is_changing_line(v)
            is_yang = v in (YOUNG_YANG, OLD_YANG)
            # 用等宽的 ━ 和全角空格保证对齐：14 个全角字符宽
            bar = "━━━━━━━━━━━━━━" if is_yang else "━━━━━━　　━━━━━━"
            prefix = " ◆ " if is_chg else "    "
            color = "#ca8a04" if is_chg else secondary
            parts.append(f'<pre style="color:{color}; font-family:楷体,KaiTi,serif; font-size:15px; '
                         f'margin:2px 0; line-height:1.6; white-space:pre;">'
                         f'{prefix}{bar}  {POS_NAMES[i]}</pre>')
        parts.append('</div><br>')

        # 本卦
        parts.append(self._fmt_hex(self._primary_data, "本  卦", "#ca8a04", changing))

        # 变卦
        if self._changed_data:
            parts.append(self._fmt_hex(self._changed_data, "变  卦", "#0d9488"))

        # 变爻
        if changing:
            parts.append(f'<div style="color:{text}; font-size:16px;">')
            parts.append('<b>变 爻 详 情</b><br>')
            for pos in changing:
                ld = self._primary_data["lines"][pos - 1]
                desc = CHANGE_DESC.get(self._lines[pos - 1], "")
                parts.append(f'  第 {pos} 爻  {ld["label"]}：{ld["text"]}<br>')
                parts.append(f'  <span style="color:#ca8a04">→ {desc}</span><br>')
                parts.append(f'  <span style="color:{dim}">{ld["xiang"]}</span><br><br>')
            parts.append('</div>')

        # 朱熹
        parts.append(self._fmt_zhuxi())

        # AI 占位
        parts.append(f'<div style="color:{dim}; font-size:11px;">')
        parts.append('<b>AI 解 读</b><br>（配置 API 密钥后点击 AI 解卦按钮）</div>')

        html = '<div style="font-size:17px;">' + "".join(parts) + '</div>'
        self.result_text.setHtml(html)

    def _fmt_hex(self, data, badge, badge_color, changing=None):
        dim = self._tc("#5e5a4e", "#3a3630")
        secondary = self._tc("#9b9788", "#2e2a25")
        p = f"""<div style="margin:12px 0;">
        <span style="color:{badge_color}; font-weight:bold;">  {badge}</span><br>
        <span style="font-size:46px; font-family:楷体,KaiTi,serif;">{data['symbol']}</span>
        <span style="font-size:23px; font-weight:bold; font-family:楷体,KaiTi,serif;">  {data['name']}</span><br>
        <span style="color:{dim}; font-size:14px;">第 {data['number']} 卦  ·  {data['pinyin']}</span><br>
        <span style="color:{dim}; font-size:14px;">上 {data['upper_trigram']}　下 {data['lower_trigram']}</span><br><br>
        <b style="font-family:楷体,KaiTi,serif; font-size:18px;">　卦　辞</b><br>{data['judgment']}<br><br>
        <b style="font-family:楷体,KaiTi,serif; font-size:18px;">　彖　传</b><br>{data['tuan_zhuan']}<br><br>
        <b style="font-family:楷体,KaiTi,serif; font-size:18px;">　大象传</b><br>{data['xiang_zhuan']}<br><br>
        <b style="font-family:楷体,KaiTi,serif; font-size:18px;">　爻　辞</b><br>"""
        for line in data["lines"]:
            is_chg = changing and line["position"] in changing
            c = "#ca8a04" if is_chg else secondary
            prefix = "◆" if is_chg else "·"
            p += f'<span style="color:{c}; font-family:楷体,KaiTi,serif;">  {prefix} {line["label"]}：{line["text"]}</span><br>'
        p += '</div>'
        return p

    def _fmt_zhuxi(self):
        n = sum(1 for v in self._lines if v in (OLD_YIN, OLD_YANG))
        rule = get_interpretation_rule(n)
        focus = get_focus_text(self._lines, self._primary_data, self._changed_data)
        return f"""<div style="margin:16px 0;">
        <b style="font-family:楷体,KaiTi,serif; font-size:16px;">断 卦 规 则</b><br>
        <span style="color:#ca8a04;">  朱熹《周易启蒙》 · {rule['rule']}</span><br>
        {rule['description']}<br><br>
        <b style="color:#ca8a04;">▽  重点看：{focus['focus_title']}</b><br>
        {focus['focus_content'].replace(chr(10), '<br>')}
        </div>"""

    def _get_question(self) -> str:
        t = self.question_edit.toPlainText().strip()
        return t if t != "例如：我最近的事业运势如何？这次考试结果会怎样？" else ""

    def _copy_result(self):
        text = self.result_text.toPlainText()
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        self.copy_btn.setText("✓ 已复制")
        QTimer.singleShot(1500, lambda: self.copy_btn.setText("📋 复制结果"))

    def _export_result(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        path, _ = QFileDialog.getSaveFileName(self, "导出卦象结果", "易经占卜结果.txt",
                                               "文本文件 (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.result_text.toPlainText())
                QMessageBox.information(self, "导出成功", f"卦象结果已保存到：\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"保存文件时出错：{e}")

    # ═══ AI ═══

    def _request_ai(self):
        if not self._current_result or not self._primary_data:
            return
        if not has_api_key():
            self.ai_status.setText("请先在「设置」中配置 API 密钥")
            return

        self.ai_btn.setEnabled(False)
        self.ai_btn.setText("解读中...")
        self.ai_status.setText("正在请求 AI 解读...")

        lines_detail = "\n".join(
            f"{l['label']}：{l['text']}" for l in self._primary_data["lines"]
        )
        changing_lines = self._current_result.get("changing_lines", [])
        changing_info = ""
        if changing_lines and self._primary_data:
            parts = [f"第{p}爻 {self._primary_data['lines'][p-1]['label']}：{self._primary_data['lines'][p-1]['text']}"
                     for p in changing_lines]
            changing_info = "\n".join(parts)

        focus = get_focus_text(
            self._current_result["lines"], self._primary_data, self._changed_data
        )
        zhuxi_rule = f"{focus['rule']}：{focus['description']}"
        zhuxi_focus = f"【{focus['focus_title']}】\n{focus['focus_content']}"

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
                text = re.sub(r'#{2,}\s*', '', result)
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
                self.ai_done.emit(text)
            except Exception as e:
                self.ai_error.emit(str(e))

        threading.Thread(target=run, daemon=True).start()

    def _format_ai(self, text: str) -> str:
        """将 AI 返回的纯文本转为格式化 HTML"""
        # 去掉 emoji
        import re as _re
        text = _re.sub(r'[\U0001F300-\U0001F9FF☀-➿⭐✀-➿️‍]', '', text)
        lines = text.split('\n')
        parts = []
        prev_empty = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if not prev_empty:
                    parts.append('<br>')
                    prev_empty = True
                continue
            prev_empty = False
            # 标题行检测：数字开头、**粗体**、或以"]" "：" 结尾的短行
            is_heading = False
            if len(stripped) <= 22 and ('：' in stripped or '：' in stripped or
                                         '启示' in stripped or '建议' in stripped or
                                         '总结' in stripped or '分析' in stripped or
                                         '趋势' in stripped or '含义' in stripped or
                                         '变化' in stripped):
                is_heading = True
            if re.match(r'^[一二三四五六七八九十\d]+[、.．）\)]', stripped):
                is_heading = True
            if stripped.startswith('**') and stripped.endswith('**'):
                stripped = stripped[2:-2]
                is_heading = True
            if is_heading:
                parts.append(f'<p style="color:#ca8a04; font-size:17px; font-weight:bold; '
                             f'margin:6px 0 1px 0; font-family:楷体,KaiTi,serif;">{stripped}</p>')
            else:
                parts.append(f'<span style="font-size:16px; line-height:1.4;">{stripped}</span><br>')
        return ''.join(parts)

    def _on_ai_done(self, text: str):
        # 去掉 emoji
        import re as _re
        text = _re.sub(r'[\U0001F300-\U0001F9FF☀-➿⭐✀-➿️‍]', '', text)
        scroll = self.result_text.verticalScrollBar().value()
        self._append_ai_html(text)
        self.result_text.verticalScrollBar().setValue(scroll)
        self._ai_text = text
        try:
            from storage.history_db import get_all_readings, update_ai_analysis
            records = get_all_readings(limit=1, offset=0)
            if records:
                update_ai_analysis(records[0]["id"], text)
        except Exception:
            pass
        self.ai_btn.setEnabled(True)
        self.ai_btn.setText("🤖  AI 解卦")
        self.ai_status.setText("✓ 解读完成")
        self._ai_text = text

    def _on_ai_error(self, msg: str):
        current = self.result_text.toHtml()
        self.result_text.setHtml(
            current +
            f'<div style="color:#c44a4a; font-size:15px; padding:8px 0;">请求失败：{msg}</div>'
        )
        self.ai_btn.setEnabled(True)
        self.ai_btn.setText("🤖  AI 解卦")
        self.ai_status.setText(f"失败：{msg}")

    def refresh_text_tags(self):
        pass  # PySide6 doesn't need tag refresh
