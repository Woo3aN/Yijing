"""全局样式定制 —— 圆角按钮 + 主题适配"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk


# 全局图片引用——防止 tkinter 垃圾回收 PhotoImage
_IMG_CACHE = []

# 需要刷新背景的 tk 控件（非 ttk，需手动适配主题）
_TK_WIDGETS = []


def register_tk_widget(widget):
    """注册需要跟随主题切换背景的 tk 控件"""
    _TK_WIDGETS.append(widget)


def get_theme_colors() -> dict:
    """从当前 ttkbootstrap 主题提取关键色"""
    style = ttk.Style()
    try:
        bg = style.colors.bg
        fg = style.colors.fg
        primary = style.colors.primary
        success = style.colors.success
        warning = style.colors.warning
        danger = style.colors.danger
        secondary = style.colors.secondary
        selectbg = style.colors.selectbg
        inputbg = style.colors.inputbg
        border = style.colors.border
    except Exception:
        # 回退 darkly 色值
        bg = "#1c1c1c"; fg = "#ffffff"; primary = "#375a7f"
        success = "#00bc8c"; warning = "#f39c12"; danger = "#e74c3c"
        secondary = "#aaaaaa"; selectbg = "#375a7f"
        inputbg = "#2b2b2b"; border = "#444444"

    return {
        "bg": bg, "fg": fg,
        "primary": primary, "primary_hover": _lighten(primary, 0.15),
        "success": success, "success_hover": _lighten(success, 0.15),
        "warning": warning, "warning_hover": _lighten(warning, 0.15),
        "danger": danger,
        "secondary": secondary,
        "inputbg": inputbg, "border": border,
        "text_dim": _dim(fg, 0.45), "text_secondary": _dim(fg, 0.65),
    }


def _lighten(hex_color: str, amount: float) -> str:
    """提亮颜色"""
    c = hex_color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return f"#{r:02x}{g:02x}{b:02x}"


def _dim(hex_color: str, amount: float) -> str:
    """变暗颜色"""
    c = hex_color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    r, g, b = int(r * amount), int(g * amount), int(b * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def get_text_colors() -> dict:
    """获取 Text 标签的文字颜色方案"""
    c = get_theme_colors()
    return {
        "h1": c["fg"], "h2": c["fg"], "h3": c["fg"],
        "body": c["fg"], "guafu": c["fg"],
        "line_default": c["text_secondary"],
        "line_changed": c["warning"],
        "highlight": c["primary"],
        "tag_primary": c["primary"], "tag_change": c["warning"],
        "warn": c["warning"], "dim": c["text_dim"],
        "sep": c["border"],
        "line_chg": c["warning"], "line_normal": c["text_secondary"],
        "placeholder": c["text_dim"],
    }


def refresh_tk_widgets():
    """主题切换后刷新所有 tk 控件背景"""
    c = get_theme_colors()
    for w in _TK_WIDGETS:
        try:
            w.configure(bg=c["inputbg"], fg=c["fg"],
                        insertbackground=c["fg"])
        except Exception:
            pass


# ═══════════════════════════════════
#  PIL 圆角按钮图片生成
# ═══════════════════════════════════

def _make_pill(width: int, height: int, color: str, outline: bool = False,
               radius: int = 8) -> Image.Image:
    scale = 2
    w, h = width * scale, height * scale
    r = radius * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if outline:
        r_hex, g_hex, b_hex = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fill = (r_hex, g_hex, b_hex, 15)
        draw.rounded_rectangle([(2, 2), (w - 3, h - 3)], radius=r,
                               fill=fill, outline=color, width=2)
    else:
        draw.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=r,
                               fill=color, outline=color, width=1)
    return img.resize((width, height), Image.LANCZOS)


class RoundedButton(tk.Canvas):
    """圆角按钮（PIL 渲染，支持主题色自动适配）"""

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
        self._radius = 8
        self._theme_color = theme_color  # "primary" / "success" / "warning"

        self._draw(hover=False)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self._draw(hover=True))
        self.bind("<Leave>", lambda e: self._draw(hover=False))

    def _get_color(self, hover: bool = False) -> str:
        """从当前主题获取对应颜色"""
        c = get_theme_colors()
        key = self._theme_color
        if hover and key in ("primary", "success", "warning"):
            return c.get(f"{key}_hover", c[key])
        return c.get(key, c["primary"])

    def _draw(self, hover: bool = False):
        self.delete("all")
        color = self._get_color(hover)
        w, h = self._btn_width, self._btn_height
        img = _make_pill(w, h, color, outline=self._outline, radius=self._radius)
        self._tkimg = ImageTk.PhotoImage(img, master=self)
        _IMG_CACHE.append(self._tkimg)
        self.create_image(0, 0, anchor="nw", image=self._tkimg)

        text_c = color if self._outline else "#ffffff"
        weight = "" if self._outline else "bold"
        self.create_text(w // 2, h // 2, text=self._text,
                         fill=text_c, font=("微软雅黑", self._font_size, weight))

    def _on_click(self, event):
        if self._command:
            self._command()

    def set_text(self, text: str):
        self._text = text
        self._draw(hover=False)

    def configure_state(self, enabled: bool):
        """启用/禁用"""
        if enabled:
            self.bind("<Button-1>", self._on_click)
            self._draw(hover=False)
        else:
            self.unbind("<Button-1>")
            self.delete("all")
            c = get_theme_colors()
            w, h = self._btn_width, self._btn_height
            img = _make_pill(w, h, c["border"], radius=self._radius)
            self._tkimg = ImageTk.PhotoImage(img, master=self)
            _IMG_CACHE.append(self._tkimg)
            self.create_image(0, 0, anchor="nw", image=self._tkimg)
            self.create_text(w // 2, h // 2, text=self._text,
                             fill=c["text_dim"],
                             font=("微软雅黑", self._font_size, "bold"))


def apply_custom_style():
    """在所有主题之上覆盖柔和样式"""
    style = ttk.Style()

    style.configure(".", font=("微软雅黑", 10))
    style.configure("TButton", padding=(14, 7), font=("微软雅黑", 10))
    for v in ("primary", "secondary", "success", "danger", "warning", "info"):
        style.configure(f"{v}.Outline.TButton", padding=(14, 7))
    style.configure("TLabelframe", relief="flat", borderwidth=1, padding=14)
    style.configure("TLabelframe.Label", font=("微软雅黑", 10, "bold"), padding=(8, 2))
    style.configure("TEntry", padding=(10, 6), font=("微软雅黑", 10))
    style.configure("TCombobox", padding=(10, 5), font=("微软雅黑", 10))
    style.configure("TNotebook.Tab", padding=(20, 10), font=("微软雅黑", 11))
    style.configure("Treeview", rowheight=34, font=("微软雅黑", 10))
    style.configure("Treeview.Heading", padding=(8, 6), font=("微软雅黑", 10, "bold"))
