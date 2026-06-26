"""历史记录数据库 —— SQLite 存储占卜记录"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Optional


def _get_db_path() -> str:
    """获取数据库文件路径"""
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    db_dir = os.path.join(appdata, "Yijing")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "history.db")


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """初始化数据库表（首次运行时创建）"""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL DEFAULT '',
            method TEXT NOT NULL CHECK(method IN ('coins', 'random')),
            created_at TEXT NOT NULL,
            lines TEXT NOT NULL,
            hexagram_number INTEGER NOT NULL,
            hexagram_name TEXT NOT NULL,
            changed_hexagram_number INTEGER,
            changed_hexagram_name TEXT,
            ai_analysis TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_reading(
    question: str,
    method: str,
    lines: list[int],
    hexagram_number: int,
    hexagram_name: str,
    changed_hexagram_number: Optional[int] = None,
    changed_hexagram_name: Optional[str] = None,
    ai_analysis: Optional[str] = None,
) -> int:
    """
    保存一条占卜记录。

    Returns:
        新记录的 ID
    """
    init_db()
    conn = _get_connection()
    cursor = conn.execute(
        """INSERT INTO readings
           (question, method, created_at, lines, hexagram_number, hexagram_name,
            changed_hexagram_number, changed_hexagram_name, ai_analysis)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            question,
            method,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            json.dumps(lines),
            hexagram_number,
            hexagram_name,
            changed_hexagram_number,
            changed_hexagram_name,
            ai_analysis,
        )
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_all_readings(limit: int = 100, offset: int = 0) -> list[dict]:
    """获取历史记录列表（按时间倒序）"""
    init_db()
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM readings ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_reading_by_id(reading_id: int) -> Optional[dict]:
    """获取单条记录"""
    init_db()
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM readings WHERE id = ?", (reading_id,)
    ).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def search_readings(keyword: str, limit: int = 50) -> list[dict]:
    """按问题关键词搜索历史记录"""
    init_db()
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM readings WHERE question LIKE ? ORDER BY created_at DESC LIMIT ?",
        (f"%{keyword}%", limit)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def delete_reading(reading_id: int) -> bool:
    """删除一条记录，返回是否成功"""
    init_db()
    conn = _get_connection()
    cursor = conn.execute("DELETE FROM readings WHERE id = ?", (reading_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def update_ai_analysis(reading_id: int, ai_text: str) -> bool:
    """更新一条记录的 AI 解读结果"""
    init_db()
    conn = _get_connection()
    cursor = conn.execute(
        "UPDATE readings SET ai_analysis = ? WHERE id = ?",
        (ai_text, reading_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def clear_all_readings() -> int:
    """清空全部历史记录，返回删除条数"""
    init_db()
    conn = _get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM readings")
    count = cursor.fetchone()[0]
    conn.execute("DELETE FROM readings")
    conn.commit()
    conn.close()
    return count


def _row_to_dict(row: sqlite3.Row) -> dict:
    """将 SQLite Row 转为普通字典"""
    d = dict(row)
    # 将 lines 从 JSON 字符串还原为列表
    if "lines" in d and isinstance(d["lines"], str):
        d["lines"] = json.loads(d["lines"])
    return d
