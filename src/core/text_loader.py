"""卦象数据加载器 —— 加载和查询 hexagrams.json"""

import json
import os
import sys
from typing import Optional

# 模块级缓存
_hexagrams: list[dict] = []
_by_number: dict[int, dict] = {}
_by_binary: dict[str, int] = {}  # binary -> number


def get_resource_path(relative_path: str) -> str:
    """获取资源文件路径，兼容开发模式和 PyInstaller 打包模式"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，资源在 _MEIPASS 临时目录
        base_path = sys._MEIPASS
    else:
        # 开发模式，相对于本文件所在目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_hexagrams() -> list[dict]:
    """加载 64 卦数据（首次调用时从 JSON 读取，之后使用缓存）"""
    global _hexagrams, _by_number, _by_binary

    if _hexagrams:
        return _hexagrams

    json_path = get_resource_path("data/hexagrams.json")
    with open(json_path, "r", encoding="utf-8") as f:
        _hexagrams = json.load(f)

    # 构建索引
    _by_number = {h["number"]: h for h in _hexagrams}
    _by_binary = {h["binary"]: h["number"] for h in _hexagrams}

    return _hexagrams


def get_hexagram(number: int) -> Optional[dict]:
    """按卦序（1-64）获取卦象数据"""
    load_hexagrams()
    return _by_number.get(number)


def get_hexagram_by_binary(binary: str) -> Optional[dict]:
    """按六位二进制字符串获取卦象数据"""
    load_hexagrams()
    number = _by_binary.get(binary)
    if number is None:
        return None
    return _by_number[number]


def get_binary_lookup() -> dict[str, int]:
    """获取 binary -> number 查找表"""
    load_hexagrams()
    return dict(_by_binary)


def get_all_hexagrams() -> list[dict]:
    """获取全部 64 卦数据"""
    load_hexagrams()
    return list(_hexagrams)
