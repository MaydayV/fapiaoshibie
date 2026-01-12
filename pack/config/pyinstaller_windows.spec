# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - Windows版本
入口: invoice_gui.py
输出: 单文件.exe
"""

import os

block_cipher = None

# 获取路径（从当前工作目录计算）
# 假设从项目根目录运行pyinstaller
project_root = os.getcwd()
pack_dir = os.path.join(project_root, 'pack')

a = Analysis(
    [os.path.join(project_root, 'invoice_gui.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        # 将核心提取模块作为数据文件打包
        (os.path.join(project_root, 'invoice_extractor.py'), '.'),
    ],
    hiddenimports=[
        'fitz',
        'openpyxl',
        'importlib',
        'importlib.util',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
    ],
    hookspath=[os.path.join(pack_dir, 'hooks')],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_path = os.path.join(pack_dir, 'resources', 'icons', 'app.ico')

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='发票提取器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if os.path.exists(icon_path) else None,
    onefile=True,  # 单文件模式
)
