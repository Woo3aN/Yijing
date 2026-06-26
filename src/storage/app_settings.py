"""应用设置管理 —— 读写 %APPDATA%/Yijing/settings.json"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class AppSettings:
    """应用设置"""
    api_key: str = ""
    api_endpoint: str = "https://api.deepseek.com"
    model_name: str = "deepseek-v4-pro"


def _get_settings_dir() -> str:
    """获取设置目录路径（%APPDATA%/Yijing/），不存在则创建"""
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    settings_dir = os.path.join(appdata, "Yijing")
    os.makedirs(settings_dir, exist_ok=True)
    return settings_dir


def _get_settings_path() -> str:
    """获取设置文件完整路径"""
    return os.path.join(_get_settings_dir(), "settings.json")


def load_settings() -> AppSettings:
    """加载设置，如文件不存在或损坏则返回默认值"""
    path = _get_settings_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AppSettings(
            api_key=data.get("api_key", ""),
            api_endpoint=data.get("api_endpoint", "https://api.deepseek.com"),
            model_name=data.get("model_name", "deepseek-v4-pro"),
        )
    except (FileNotFoundError, json.JSONDecodeError):
        return AppSettings()


def save_settings(settings: AppSettings) -> None:
    """保存设置到文件"""
    path = _get_settings_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(settings), f, ensure_ascii=False, indent=2)


def has_api_key() -> bool:
    """检查是否已配置 API Key"""
    settings = load_settings()
    return bool(settings.api_key.strip())
