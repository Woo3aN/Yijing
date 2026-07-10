"""全局样式 — 墨金配色 · 4pt 间距 · 楷体层级"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk

_IMG_CACHE = []
_TK_WIDGETS = []
_BTN_CACHE = []  # 圆角按钮引用，主题切换时需重绘


def register_tk_widget(widget):
    _TK_WIDGETS.append(widget)


# ═══════════════════════════════════
#  墨金配色（暗 / 亮两套）
# ═══════════════════════════════════

DARK = {
    "bg": "#161511", "surface": "#1e1d18",
    "border": "#2e2c24", "text": "#f0ece0",
    "text_secondary": "#9b9788", "text_dim": "#5e5a4e",
    "primary": "#ca8a04", "primary_hover": "#e09e08",
    "success": "#0d9488", "success_hover": "#0faaa0",
    "warning": "#ca8a04", "warning_hover": "#e09e08",
    "danger": "#c44a4a",
    "inputbg": "#1e1d18", "radius": 8,
}

LIGHT = {
    "bg": "#fefcf4", "surface": "#faf7ed",
    "border": "#e8e2d0", "text": "#1c1915",
    "text_secondary": "#7a7568", "text_dim": "#b0a998",
    "primary": "#b07d02", "primary_hover": "#c89008",
    "success": "#0f766e", "success_hover": "#12887e",
    "warning": "#b07d02", "warning_hover": "#c89008",
    "danger": "#c44a4a",
    "inputbg": "#faf7ed", "radius": 8,
}


def _palette() -> dict:
    """根据当前 ttkbootstrap 主题亮度返回对应色板"""
    try:
        bg = ttk.Style().colors.bg
    except Exception:
        bg = "#161511"
    r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
    return DARK if (r * 299 + g * 587 + b * 114) / 1000 < 128 else LIGHT


def get_theme_colors() -> dict:
    """返回当前主题色（供外部使用）"""
    return _palette().copy()


def get_text_colors() -> dict:
    """返回 Text 标签颜色方案"""
    p = _palette()
    return {
        "h1": p["text"], "h2": p["text"], "h3": p["text"],
        "body": p["text"], "guafu": p["text"],
        "line_default": p["text_secondary"], "line_changed": p["warning"],
        "highlight": p["primary"], "tag_primary": p["primary"],
        "tag_change": p["warning"], "warn": p["warning"],
        "dim": p["text_dim"], "sep": p["border"],
        "line_chg": p["warning"], "line_normal": p["text_secondary"],
        "placeholder": p["text_dim"],
    }


def _lighten(hex_color: str, amount: float) -> str:
    c = hex_color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return f"#{min(255, int(r+(255-r)*amount)):02x}{min(255, int(g+(255-g)*amount)):02x}{min(255, int(b+(255-b)*amount)):02x}"


def refresh_tk_widgets():
    """主题切换后重绘 tk 控件背景 + 圆角按钮"""
    p = _palette()
    for w in _TK_WIDGETS:
        try:
            w.configure(bg=p["inputbg"], fg=p["text"], insertbackground=p["text"])
        except Exception:
            pass
    for btn in _BTN_CACHE:
        try:
            btn.refresh()
        except Exception:
            pass


# ═══════════════════════════════════
#  圆角按钮（PIL 渲染）
# ═══════════════════════════════════

def _draw_pill(w, h, color: str, outline: bool, radius: int) -> Image.Image:
    scale = 2
    W, H, R = w * scale, h * scale, radius * scale
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if outline:
        rc = [int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)]
        draw.rounded_rectangle([(2, 2), (W - 3, H - 3)], radius=R,
                               fill=(*rc, 16), outline=color, width=2)
    else:
        draw.rounded_rectangle([(0, 0), (W - 1, H - 1)], radius=R,
                               fill=color, outline=color, width=1)
    return img.resize((w, h), Image.LANCZOS)


class RoundedButton(tk.Canvas):
    """圆角按钮 — 跟随主题色自动适配"""

    def __init__(self, parent, text: str, theme_color: str = "primary",
                 outline: bool = False, font_size: int = 11,
                 width: int = 0, height: int = 38, command=None, **kw):
        self._btn_width = width if width > 0 else max(len(text) * 20 + 40, 110)
        self._btn_height = height
        super().__init__(parent, width=self._btn_width, height=self._btn_height,
                         highlightthickness=0, bd=0, **kw)
        register_tk_widget(self)
        self._text = text
        self._outline = outline
        self._font_size = font_size
        self._command = command
        self._theme_color = theme_color
        self._radius = _palette()["radius"]
        _BTN_CACHE.append(self)
        self._draw(hover=False)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self._draw(hover=True))
        self.bind("<Leave>", lambda e: self._draw(hover=False))

    def _get_color(self, hover=False) -> str:
        p = _palette()
        key = self._theme_color
        if hover and key in ("primary", "success", "warning"):
            return p.get(f"{key}_hover", p[key])
        return p.get(key, p["primary"])

    def _draw(self, hover=False):
        self.delete("all")
        p = _palette()
        color = self._get_color(hover)
        w, h = self._btn_width, self._btn_height
        img = _draw_pill(w, h, color, self._outline, p["radius"])
        self._tkimg = ImageTk.PhotoImage(img, master=self)
        _IMG_CACHE.append(self._tkimg)
        self.create_image(0, 0, anchor="nw", image=self._tkimg)
        text_c = color if self._outline else p.get("text", "#ffffff")
        wt = "" if self._outline else "bold"
        self.create_text(w // 2, h // 2, text=self._text,
                         fill=text_c, font=("微软雅黑", self._font_size, wt))

    def _on_click(self, event):
        if self._command:
            self._command()

    def refresh(self):
        """主题切换后重绘按钮（使用新主题色）"""
        self._radius = _palette()["radius"]
        self._draw(hover=False)

    def set_text(self, text: str):
        self._text = text
        self._draw(hover=False)

    def configure_state(self, enabled: bool):
        if enabled:
            self.bind("<Button-1>", self._on_click)
            self._draw(hover=False)
        else:
            self.unbind("<Button-1>")
            self.delete("all")
            p = _palette()
            w, h = self._btn_width, self._btn_height
            img = _draw_pill(w, h, p["border"], False, p["radius"])
            self._tkimg = ImageTk.PhotoImage(img, master=self)
            _IMG_CACHE.append(self._tkimg)
            self.create_image(0, 0, anchor="nw", image=self._tkimg)
            self.create_text(w // 2, h // 2, text=self._text,
                             fill=p["text_dim"],
                             font=("微软雅黑", self._font_size, "bold"))


# ═══════════════════════════════════
#  全局 ttk 样式（4pt 间距）
# ═══════════════════════════════════

def apply_custom_style():
    """在所有 ttkbootstrap 主题之上叠加自定义样式"""
    style = ttk.Style()
    p = _palette()

    style.configure(".", font=("微软雅黑", 10))

    # 按钮：加大内边距
    style.configure("TButton", padding=(20, 9), font=("微软雅黑", 10))
    for v in ("primary", "secondary", "success", "danger", "warning", "info"):
        style.configure(f"{v}.Outline.TButton", padding=(20, 9))

    # 卡片面板
    style.configure("TLabelframe", relief="flat", borderwidth=1, padding=20)
    style.configure("TLabelframe.Label",
                    font=("微软雅黑", 10, "bold"), padding=(12, 3))

    # 输入框
    style.configure("TEntry", padding=(12, 7), font=("微软雅黑", 10))
    style.configure("TCombobox", padding=(12, 6), font=("微软雅黑", 10))

    # Tab
    style.configure("TNotebook.Tab", padding=(24, 12), font=("微软雅黑", 11))
    style.configure("TNotebook", padding=8)

    # Treeview
    style.configure("Treeview", rowheight=36, font=("微软雅黑", 10))
    style.configure("Treeview.Heading", padding=(10, 7),
                    font=("微软雅黑", 10, "bold"))

    # TFrame —— 用色板色替代主题默认灰
    p = _palette()
    style.configure("TFrame", background=p["bg"])


# ═══════════════════════════════════
#  渐变背景 Canvas
# ═══════════════════════════════════

class GradientBackground(tk.Canvas):
    """全屏暖色渐变背景"""

    def __init__(self, parent, **kw):
        super().__init__(parent, highlightthickness=0, bd=0, **kw)
        register_tk_widget(self)
        self._redraw()

    def _redraw(self):
        self.delete("all")
        p = _palette()
        w = self.winfo_width() or 960
        h = self.winfo_height() or 740

        # 从上到下：略深 → 略亮，模拟光照
        top = p["bg"]
        bot = _lighten(p["bg"], 0.06)
        img = Image.new("RGBA", (w, h))
        draw = ImageDraw.Draw(img)
        for y in range(h):
            t = y / h
            r1, g1, b1 = int(top[1:3], 16), int(top[3:5], 16), int(top[5:7], 16)
            r2, g2, b2 = int(bot[1:3], 16), int(bot[3:5], 16), int(bot[5:7], 16)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        self._bg_img = ImageTk.PhotoImage(img, master=self)
        _IMG_CACHE.append(self._bg_img)
        self.create_image(0, 0, anchor="nw", image=self._bg_img)

    def refresh(self):
        self._redraw()


# ═══════════════════════════════════
#  圆角卡片（自绘，替代 LabelFrame）
# ═══════════════════════════════════

class CardCanvas(tk.Canvas):
    """带阴影 + 标题的圆角卡片"""

    def __init__(self, parent, title: str = "", height: int = 200, **kw):
        super().__init__(parent, highlightthickness=0, bd=0, height=height, **kw)
        register_tk_widget(self)
        self._title = title
        self._card_height = height
        self._redraw()
        self.bind("<Configure>", lambda e: self._redraw())

    def _redraw(self, event=None):
        self.delete("all")
        p = _palette()
        w = self.winfo_width() or 300
        h = self.winfo_height() or self._card_height
        if w < 10:
            return
        r = 12  # 卡片圆角

        scale = 2
        W, H, R = w * scale, h * scale, r * scale
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 阴影层（偏移 + 半透明）
        shadow_color = (0, 0, 0, 30)
        draw.rounded_rectangle([(6, 8), (W - 3, H + 1)], radius=R,
                               fill=shadow_color, outline=shadow_color, width=1)

        # 卡片主体
        card_bg = _lighten(p["bg"], 0.04)
        draw.rounded_rectangle([(0, 2), (W - 2, H - 2)], radius=R,
                               fill=card_bg, outline=p["border"], width=2)

        img = img.resize((w, h), Image.LANCZOS)
        self._card_img = ImageTk.PhotoImage(img, master=self)
        _IMG_CACHE.append(self._card_img)
        self.create_image(0, 0, anchor="nw", image=self._card_img)

        # 标题文字（左上角，带装饰点）
        if self._title:
            self.create_text(22, 18, anchor="w", text=f"●  {self._title}",
                             fill=p["text"], font=("微软雅黑", 11, "bold"))

    def refresh(self):
        self._redraw()


# ═══════════════════════════════════
#  自定义导航栏（替代 Notebook）
# ═══════════════════════════════════

class NavBar(tk.Frame):
    """顶部导航栏 — 三个圆角导航按钮"""

    def __init__(self, parent, on_change=None, **kw):
        super().__init__(parent, **kw)
        self._on_change = on_change
        self._buttons = {}
        self._active = None

        p = _palette()
        self.configure(bg=p["surface"])

        tabs = [("divination", "问  卦"), ("history", "历  史"), ("settings", "设  置")]
        for key, label in tabs:
            btn = RoundedButton(self, text=label, theme_color="primary",
                                outline=True, font_size=10, height=34,
                                command=lambda k=key: self._select(k))
            btn.pack(side="left", padx=4)
            self._buttons[key] = btn

        self._select("divination")

    def _select(self, key: str):
        self._active = key
        for k, btn in self._buttons.items():
            btn._outline = (k != key)
            btn._draw(hover=False)
        if self._on_change:
            self._on_change(key)
