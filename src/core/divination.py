"""起卦算法 —— 三铜钱法和随机数法"""

import random
from typing import Optional

from .text_loader import get_binary_lookup

# 爻值常量
OLD_YIN = 6     # 老阴（变爻）
YOUNG_YANG = 7  # 少阳（不变）
YOUNG_YIN = 8   # 少阴（不变）
OLD_YANG = 9    # 老阳（变爻）

# 中文标签
LINE_LABELS = {
    6: "老阴",
    7: "少阳",
    8: "少阴",
    9: "老阳",
}


def coin_method() -> list[int]:
    """
    三铜钱法起卦。
    模拟扔三枚铜钱 6 次，从初爻到上爻。

    每枚铜钱：正面=1（阳），反面=0（阴）
    三枚之和：
      0 → 老阴(6)
      1 → 少阳(7)
      2 → 少阴(8)
      3 → 老阳(9)

    Returns:
        长度为 6 的列表 [初爻值, ..., 上爻值]
    """
    lines = []
    for _ in range(6):
        coin1 = random.randint(0, 1)
        coin2 = random.randint(0, 1)
        coin3 = random.randint(0, 1)
        heads = coin1 + coin2 + coin3

        if heads == 0:
            lines.append(OLD_YIN)      # 6 老阴
        elif heads == 1:
            lines.append(YOUNG_YANG)   # 7 少阳
        elif heads == 2:
            lines.append(YOUNG_YIN)    # 8 少阴
        else:  # heads == 3
            lines.append(OLD_YANG)     # 9 老阳
    return lines


def random_method() -> list[int]:
    """
    随机数法起卦。
    直接从 [6, 7, 8, 9] 中随机抽取 6 次。

    概率分布与三铜钱法接近：
      老阴(6): 1/8, 少阳(7): 3/8, 少阴(8): 3/8, 老阳(9): 1/8

    Returns:
        长度为 6 的列表 [初爻值, ..., 上爻值]
    """
    # 权重模拟真实铜钱概率
    return random.choices(
        [OLD_YIN, YOUNG_YANG, YOUNG_YIN, OLD_YANG],
        weights=[1, 3, 3, 1],
        k=6
    )


def coin_toss_details() -> list[dict]:
    """
    三铜钱法的详细抛掷过程（用于动画展示）。

    Returns:
        [{toss_num, coins: [0|1, 0|1, 0|1], heads, line_value, label, is_changing}, ...]
    """
    details = []
    for i in range(6):
        coins = [random.randint(0, 1) for _ in range(3)]
        heads = sum(coins)

        if heads == 0:
            value = OLD_YIN
        elif heads == 1:
            value = YOUNG_YANG
        elif heads == 2:
            value = YOUNG_YIN
        else:
            value = OLD_YANG

        details.append({
            "toss_num": i + 1,
            "coins": coins,           # [0, 1, 1] 表示 反面反面正面
            "heads": heads,
            "line_value": value,
            "label": LINE_LABELS[value],
            "is_changing": value in (OLD_YIN, OLD_YANG),
        })
    return details


def lines_to_binary(lines: list[int]) -> tuple[str, Optional[str], list[int]]:
    """
    将六个爻值转换为本卦和变卦的二进制字符串。

    Args:
        lines: 六个爻值 [初爻, ..., 上爻]

    Returns:
        (本卦binary, 变卦binary或None, 变爻位置列表[1-based])
    """
    # 本卦：6/8→0(阴), 7/9→1(阳)
    primary = "".join("1" if v in (YOUNG_YANG, OLD_YANG) else "0" for v in lines)

    # 变卦：翻转变爻（6→1, 9→0），不变爻保持
    changing_lines = []
    changed_list = list(primary)
    for i, v in enumerate(lines):
        if v == OLD_YIN:   # 6 老阴 → 阳
            changed_list[i] = "1"
            changing_lines.append(i + 1)  # 1-based
        elif v == OLD_YANG:  # 9 老阳 → 阴
            changed_list[i] = "0"
            changing_lines.append(i + 1)

    changed = "".join(changed_list)

    if changed == primary:
        return primary, None, changing_lines  # 无变卦

    return primary, changed, changing_lines


def perform_divination(method: str = "coins") -> dict:
    """
    执行一次完整的占卜。

    Args:
        method: "coins" 或 "random"

    Returns:
        {
            "lines": [int, ...],          # 六个爻值
            "primary_binary": str,         # 本卦二进制
            "changed_binary": str|None,    # 变卦二进制
            "changing_lines": [int, ...],  # 变爻位置 (1-based)
            "primary_number": int,         # 本卦序号
            "changed_number": int|None,    # 变卦序号
        }
    """
    if method == "coins":
        lines = coin_method()
    else:
        lines = random_method()

    primary_bin, changed_bin, changing = lines_to_binary(lines)

    lookup = get_binary_lookup()
    primary_num = lookup[primary_bin]
    changed_num = lookup[changed_bin] if changed_bin else None

    return {
        "lines": lines,
        "primary_binary": primary_bin,
        "changed_binary": changed_bin,
        "changing_lines": changing,
        "primary_number": primary_num,
        "changed_number": changed_num,
    }


def line_value_to_chinese(value: int) -> str:
    """爻值转中文标签"""
    return LINE_LABELS.get(value, "未知")


def is_changing_line(value: int) -> bool:
    """判断是否为变爻"""
    return value in (OLD_YIN, OLD_YANG)


# ════════════════════════════════════════════
#  朱熹《周易启蒙》断卦规则
# ════════════════════════════════════════════

def get_interpretation_rule(num_changing: int) -> dict:
    """
    根据变爻数量，返回朱熹断卦规则。

    Returns:
        {
            "rule": "规则名称",
            "description": "详细说明",
            "method": "primary_judgment | primary_line | changed_unchanged_line | changed_judgment | qian_kun_special",
        }
    """
    rules = {
        0: {
            "rule": "六爻皆静（无变爻）",
            "description": "用本卦卦辞断事。本卦代表当前状态，卦辞直接对应所问之事。",
            "method": "primary_judgment",
        },
        1: {
            "rule": "一爻变",
            "description": "用本卦变爻的爻辞断事。这一爻的变化是事情的关键所在。",
            "method": "primary_line",
        },
        2: {
            "rule": "二爻变",
            "description": "用本卦两个变爻的爻辞断事，以位置在上面的那个变爻为主（上爻为君，下爻为臣）。",
            "method": "primary_two_lines",
        },
        3: {
            "rule": "三爻变",
            "description": "用本卦卦辞并结合变卦卦辞综合判断。本卦为体（当前），变卦为用（发展）。",
            "method": "both_judgments",
        },
        4: {
            "rule": "四爻变",
            "description": "用变卦中两个不变爻的爻辞断事，以位置在下面的那个不变爻为主。",
            "method": "changed_unchanged_lines",
        },
        5: {
            "rule": "五爻变",
            "description": "用变卦中唯一不变爻的爻辞断事。众爻皆变，唯此一爻守静，是事态的关键。",
            "method": "changed_single_unchanged",
        },
        6: {
            "rule": "六爻皆变",
            "description": "用变卦卦辞断事。乾坤二卦例外：乾卦用「用九：见群龙无首，吉」，坤卦用「用六：利永贞」。",
            "method": "all_changed",
        },
    }
    return rules.get(num_changing, rules[0])


def get_focus_text(
    lines: list[int],
    primary_data: dict,
    changed_data: dict | None,
) -> dict:
    """
    根据朱熹断卦规则，提取需要重点关注的内容。

    Returns:
        {
            "rule": "规则名称",
            "description": "规则说明",
            "focus_title": "重点看什么",
            "focus_content": "关键文本内容",
        }
    """
    changing_lines = [i + 1 for i, v in enumerate(lines) if v in (OLD_YIN, OLD_YANG)]
    n = len(changing_lines)
    rule = get_interpretation_rule(n)

    result = {
        "rule": rule["rule"],
        "description": rule["description"],
        "focus_title": "",
        "focus_content": "",
    }

    if rule["method"] == "primary_judgment":
        result["focus_title"] = f"本卦「{primary_data['name']}」卦辞"
        result["focus_content"] = (
            f"{primary_data['symbol']} {primary_data['name']}　{primary_data['judgment']}\n\n"
            f"{primary_data['tuan_zhuan']}\n\n"
            f"{primary_data['xiang_zhuan']}"
        )

    elif rule["method"] == "primary_line":
        pos = changing_lines[0]
        ld = primary_data["lines"][pos - 1]
        result["focus_title"] = f"本卦「{primary_data['name']}」{ld['label']}爻辞"
        result["focus_content"] = f"{ld['text']}\n\n{ld['xiang']}"

    elif rule["method"] == "primary_two_lines":
        # 两个变爻，上面的为主
        upper_pos = max(changing_lines)
        lower_pos = min(changing_lines)
        upper_ld = primary_data["lines"][upper_pos - 1]
        lower_ld = primary_data["lines"][lower_pos - 1]
        result["focus_title"] = (
            f"本卦「{primary_data['name']}」{lower_ld['label']}与{upper_ld['label']}爻辞"
        )
        result["focus_content"] = (
            f"【主】{upper_ld['label']}：{upper_ld['text']}\n{upper_ld['xiang']}\n\n"
            f"【次】{lower_ld['label']}：{lower_ld['text']}\n{lower_ld['xiang']}"
        )

    elif rule["method"] == "both_judgments":
        result["focus_title"] = "本卦与变卦卦辞综合"
        text = (
            f"【本卦 {primary_data['name']}】\n"
            f"{primary_data['judgment']}\n\n"
        )
        if changed_data:
            text += (
                f"【变卦 {changed_data['name']}】\n"
                f"{changed_data['judgment']}\n"
            )
        result["focus_content"] = text

    elif rule["method"] == "changed_unchanged_lines":
        # 变卦中不变爻（在原 lines 中值为 7 或 8 的位置）
        unchanged_positions = [
            i + 1 for i, v in enumerate(lines) if v in (YOUNG_YANG, YOUNG_YIN)
        ]
        lower_pos = min(unchanged_positions)
        upper_pos = max(unchanged_positions)
        lower_ld = changed_data["lines"][lower_pos - 1]
        upper_ld = changed_data["lines"][upper_pos - 1]
        result["focus_title"] = (
            f"变卦「{changed_data['name']}」不变之爻：{lower_ld['label']}与{upper_ld['label']}"
        )
        result["focus_content"] = (
            f"【主】{lower_ld['label']}：{lower_ld['text']}\n{lower_ld['xiang']}\n\n"
            f"【次】{upper_ld['label']}：{upper_ld['text']}\n{upper_ld['xiang']}"
        )

    elif rule["method"] == "changed_single_unchanged":
        unchanged_pos = [i + 1 for i, v in enumerate(lines) if v in (YOUNG_YANG, YOUNG_YIN)][0]
        ld = changed_data["lines"][unchanged_pos - 1]
        result["focus_title"] = f"变卦「{changed_data['name']}」唯一不变爻 {ld['label']}"
        result["focus_content"] = f"{ld['text']}\n\n{ld['xiang']}"

    elif rule["method"] == "all_changed":
        if primary_data["number"] == 1:  # 乾卦
            result["focus_title"] = "乾卦六爻皆变 — 用九"
            result["focus_content"] = "用九：见群龙无首，吉。\n\n《象》曰：用九，天德不可为首也。"
        elif primary_data["number"] == 2:  # 坤卦
            result["focus_title"] = "坤卦六爻皆变 — 用六"
            result["focus_content"] = "用六：利永贞。\n\n《象》曰：用六永贞，以大终也。"
        elif changed_data:
            result["focus_title"] = f"变卦「{changed_data['name']}」卦辞"
            result["focus_content"] = (
                f"{changed_data['judgment']}\n\n"
                f"{changed_data['tuan_zhuan']}\n\n"
                f"{changed_data['xiang_zhuan']}"
            )

    return result
