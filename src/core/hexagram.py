"""卦象数据模型"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LineText:
    """一爻的文本"""
    position: int        # 1-6，从下往上
    label: str           # 初九、六二 等
    text: str            # 爻辞
    xiang: str           # 小象传


@dataclass
class Hexagram:
    """一个卦的完整数据"""
    number: int                      # 卦序 1-64
    binary: str                      # 六位二进制 "111111"
    name: str                        # 卦名 "乾"
    pinyin: str                      # 拼音
    symbol: str                      # Unicode 卦符 "䷀"
    upper_trigram: str               # 上卦
    lower_trigram: str               # 下卦
    judgment: str                    # 卦辞
    tuan_zhuan: str                  # 彖传
    xiang_zhuan: str                 # 大象传
    lines: list[LineText] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        """完整卦名，如 '乾为天'"""
        return f"{self.lower_trigram}为{self.upper_trigram}" if self.lower_trigram != self.upper_trigram else f"{self.name}为{self.name}"

    @property
    def changing_line_indices(self) -> list[int]:
        """变爻的位置列表（1-based）— 需要外部传入 lines 值时使用"""
        return []


def hexagram_from_dict(data: dict) -> Hexagram:
    """从字典创建 Hexagram 对象"""
    lines = [
        LineText(
            position=line["position"],
            label=line["label"],
            text=line["text"],
            xiang=line["xiang"]
        )
        for line in data["lines"]
    ]
    return Hexagram(
        number=data["number"],
        binary=data["binary"],
        name=data["name"],
        pinyin=data["pinyin"],
        symbol=data["symbol"],
        upper_trigram=data["upper_trigram"],
        lower_trigram=data["lower_trigram"],
        judgment=data["judgment"],
        tuan_zhuan=data["tuan_zhuan"],
        xiang_zhuan=data["xiang_zhuan"],
        lines=lines,
    )
