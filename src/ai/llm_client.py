"""大模型客户端 —— 调用 DeepSeek 等 OpenAI 兼容接口进行解卦"""

from typing import Iterator

from openai import OpenAI

from storage.app_settings import load_settings, has_api_key


def _build_prompt(question: str, hexagram_name: str, hexagram_symbol: str,
                  judgment: str, tuan_zhuan: str, xiang_zhuan: str,
                  changed_name: str | None, changed_symbol: str | None,
                  changing_info: str, lines_detail: str,
                  zhuxi_rule: str = "", zhuxi_focus: str = "") -> str:
    """构建发送给大模型的提示词"""
    prompt = f"""你是一位精通《周易》的占卜师。请根据以下信息为用户解卦。

【用户的问题】
{question}

【占卜结果】
本卦：{hexagram_symbol} {hexagram_name}
卦辞：{judgment}
《彖传》：{tuan_zhuan}
《大象传》：{xiang_zhuan}
"""

    if changed_name:
        prompt += f"""
变卦：{changed_symbol} {changed_name}
（变卦代表事情的发展方向）

变爻详情：
{changing_info}
"""

    prompt += f"""
各爻辞：
{lines_detail}
"""

    if zhuxi_rule:
        prompt += f"""
【朱熹《周易启蒙》断卦规则】
规则：{zhuxi_rule}
重点参考文本：
{zhuxi_focus}
"""

    prompt += """
请用简洁流畅的中文，结合卦辞和爻辞（如有朱熹断卦规则，严格按其指示的重点文本分析），针对用户的问题进行解读。内容包括：
1. 本卦对用户问题的启示
2. 如有变爻，变爻的特别含义
3. 如有变卦，从本卦到变卦代表的变化趋势
4. 给用户的综合建议

请控制在 500 字以内，语言通俗易懂。"""

    return prompt


def analyze(
    question: str,
    hexagram_name: str,
    hexagram_symbol: str,
    judgment: str,
    tuan_zhuan: str,
    xiang_zhuan: str,
    lines: list[int],
    lines_detail: str,
    changed_name: str | None = None,
    changed_symbol: str | None = None,
    changing_lines: list[int] | None = None,
    changing_info: str = "",
    zhuxi_rule: str = "",
    zhuxi_focus: str = "",
) -> str:
    """
    调用大模型进行解卦分析。

    Args:
        question: 用户问题
        hexagram_name: 本卦名
        hexagram_symbol: 本卦符号
        judgment: 卦辞
        tuan_zhuan: 彖传
        xiang_zhuan: 大象传
        lines: 六爻值
        lines_detail: 变爻详情文本
        changed_name: 变卦名
        changed_symbol: 变卦符号
        changing_lines: 变爻位置列表
        changing_info: 变爻详情文本

    Returns:
        大模型的解读文本

    Raises:
        ValueError: 未配置 API Key
        Exception: 网络或 API 调用失败
    """
    if not has_api_key():
        raise ValueError("请先在「设置」中配置 API 密钥")

    settings = load_settings()

    client = OpenAI(
        api_key=settings.api_key,
        base_url=settings.api_endpoint,
    )

    prompt = _build_prompt(
        question=question,
        hexagram_name=hexagram_name,
        hexagram_symbol=hexagram_symbol,
        judgment=judgment,
        tuan_zhuan=tuan_zhuan,
        xiang_zhuan=xiang_zhuan,
        changed_name=changed_name,
        changed_symbol=changed_symbol,
        changing_info=changing_info,
        lines_detail=lines_detail,
        zhuxi_rule=zhuxi_rule,
        zhuxi_focus=zhuxi_focus,
    )

    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000,
        timeout=60,
    )

    return response.choices[0].message.content


def analyze_stream(**kwargs) -> Iterator[str]:
    """
    流式调用大模型进行解卦分析，逐块返回文本。

    参数同 analyze() 函数。
    用法：
        for chunk in analyze_stream(question=..., ...):
            print(chunk, end="", flush=True)
    """
    if not has_api_key():
        raise ValueError("请先在「设置」中配置 API 密钥")

    settings = load_settings()

    client = OpenAI(
        api_key=settings.api_key,
        base_url=settings.api_endpoint,
    )

    # 只提取 _build_prompt 需要的参数
    prompt = _build_prompt(
        question=kwargs.get("question", ""),
        hexagram_name=kwargs.get("hexagram_name", ""),
        hexagram_symbol=kwargs.get("hexagram_symbol", ""),
        judgment=kwargs.get("judgment", ""),
        tuan_zhuan=kwargs.get("tuan_zhuan", ""),
        xiang_zhuan=kwargs.get("xiang_zhuan", ""),
        changed_name=kwargs.get("changed_name"),
        changed_symbol=kwargs.get("changed_symbol"),
        changing_info=kwargs.get("changing_info", ""),
        lines_detail=kwargs.get("lines_detail", ""),
        zhuxi_rule=kwargs.get("zhuxi_rule", ""),
        zhuxi_focus=kwargs.get("zhuxi_focus", ""),
    )

    stream = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000,
        timeout=60,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta is not None and delta.content is not None:
            yield delta.content


def test_connection() -> tuple[bool, str]:
    """
    测试 API 连接是否正常。

    Returns:
        (是否成功, 消息)
    """
    if not has_api_key():
        return False, "未配置 API 密钥"

    settings = load_settings()

    try:
        client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.api_endpoint,
        )
        response = client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {"role": "user", "content": "你好，请回复一个字：通"}
            ],
            max_tokens=10,
            timeout=15,
        )
        return True, "连接成功！"
    except Exception as e:
        return False, f"连接失败：{str(e)}"
