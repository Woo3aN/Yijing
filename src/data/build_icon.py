"""生成传统八卦图标 —— 256x256 ICO（含 PNG 条目，兼容 Win10/11）"""
import math
import struct
import io
from PIL import Image, ImageDraw

SIZE = 256
CENTER = SIZE // 2
R = 110

# 颜色
BG = (30, 30, 40)
YIN_FILL = (20, 20, 30)
YANG_FILL = (240, 240, 245)
BORDER = (180, 170, 140)
TRIGRAM_COLOR = (220, 210, 180)
DOT_COLOR_YANG = (240, 240, 245)
DOT_COLOR_YIN = (20, 20, 30)

# 先天八卦：(卦名, 爻序, 角度)
TRIGRAMS = [
    ("乾", [1,1,1], -90), ("兑", [1,1,0], -45),
    ("离", [1,0,1], 0),   ("震", [1,0,0], 45),
    ("坤", [0,0,0], 90),  ("艮", [0,0,1], 135),
    ("坎", [0,1,0], 180), ("巽", [0,1,1], -135),
]


def draw_yin_yang(draw, cx, cy, r):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=None, outline=BORDER, width=3)
    draw.pieslice([cx-r, cy-r, cx+r, cy+r], start=90, end=270, fill=YANG_FILL)
    draw.pieslice([cx-r, cy-r, cx+r, cy+r], start=270, end=90, fill=YIN_FILL)
    hr, sr = r//2, r//6
    draw.ellipse([cx-hr, cy-r, cx+hr, cy], fill=YIN_FILL)
    draw.ellipse([cx-sr, cy-hr-sr, cx+sr, cy-hr+sr], fill=DOT_COLOR_YANG)
    draw.ellipse([cx-hr, cy, cx+hr, cy+r], fill=YANG_FILL)
    draw.ellipse([cx-sr, cy+hr-sr, cx+sr, cy+hr+sr], fill=DOT_COLOR_YIN)


def draw_trigram(draw, cx, cy, lines, angle_deg):
    rad = math.radians(angle_deg)
    tc_x = cx + 88 * math.cos(rad)
    tc_y = cy - 88 * math.sin(rad)
    bw, bh, gap, yg = 20, 5, 4, 8
    th = 3*bh + 2*gap
    sy = tc_y - th//2
    for i, is_yang in enumerate(lines):
        y = sy + i*(bh+gap)
        if is_yang:
            draw.rectangle([tc_x-bw, y, tc_x+bw, y+bh], fill=TRIGRAM_COLOR)
        else:
            h = (bw-yg)//2
            draw.rectangle([tc_x-bw, y, tc_x-bw+h, y+bh], fill=TRIGRAM_COLOR)
            draw.rectangle([tc_x+bw-h, y, tc_x+bw, y+bh], fill=TRIGRAM_COLOR)


def _write_ico(png_data_dict: dict[int, bytes], path: str):
    """手动构建 ICO 文件，每个条目使用 PNG 数据（Win10/11 Explorer 标准）"""
    sizes = sorted(png_data_dict.keys(), reverse=True)
    entries = []
    offset = 6 + 16 * len(sizes)  # header(6) + entry(16)*N

    for s in sizes:
        data = png_data_dict[s]
        # 256px 在 ICO 中用 0 表示
        w = 0 if s >= 256 else s
        h = 0 if s >= 256 else s
        entries.append(struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(data), offset))
        offset += len(data)

    header = struct.pack('<HHH', 0, 1, len(sizes))

    with open(path, 'wb') as f:
        f.write(header)
        for e in entries:
            f.write(e)
        for s in sizes:
            f.write(png_data_dict[s])


def build_icon():
    img = Image.new("RGBA", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)
    draw.ellipse([CENTER-R-10, CENTER-R-10, CENTER+R+10, CENTER+R+10],
                 fill=None, outline=BORDER, width=2)
    draw_yin_yang(draw, CENTER, CENTER, R)
    for _name, lines, angle in TRIGRAMS:
        draw_trigram(draw, CENTER, CENTER, lines, angle)

    # 保存 PNG（供 iconphoto 用）
    img.save("assets/icon.png")

    # 生成各尺寸 PNG 数据并写入 ICO
    ico_sizes = [256, 128, 64, 48, 32, 16]
    png_data = {}
    for s in ico_sizes:
        buf = io.BytesIO()
        img.resize((s, s), Image.LANCZOS).save(buf, format="PNG")
        png_data[s] = buf.getvalue()

    _write_ico(png_data, "assets/icon.ico")
    print("Icon generated: assets/icon.ico")


if __name__ == "__main__":
    build_icon()
