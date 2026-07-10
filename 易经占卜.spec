# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置 —— 易经占卜"""

import sys
from pathlib import Path

# 项目根目录（SPECPATH 由 PyInstaller 在 spec 执行上下文中提供）
ROOT = Path(SPECPATH)

a = Analysis(
    # 入口脚本
    [str(ROOT / 'src' / 'main.py')],
    pathex=[str(ROOT / 'src')],
    binaries=[],
    datas=[
        # hexagrams.json → 运行时 data/ 目录
        (str(ROOT / 'src' / 'data' / 'hexagrams.json'), 'data'),
        # 图标文件 → 运行时 assets/ 目录
        (str(ROOT / 'assets' / 'icon.ico'), 'assets'),
        (str(ROOT / 'assets' / 'icon.png'), 'assets'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PIL',
        'openai',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'build_hexagrams',  # 排除构建工具
        'matplotlib',
        'numpy',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Yijing',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # 不显示命令行窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / 'assets' / 'icon.ico'),
)
