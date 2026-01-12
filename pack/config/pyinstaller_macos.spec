# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller配置文件 - macOS版本
入口: invoice_macos_dialog.py
输出: .app bundle
"""

import os

block_cipher = None

# 获取路径（从当前工作目录计算）
# 假设从项目根目录运行pyinstaller
project_root = os.getcwd()
pack_dir = os.path.join(project_root, 'pack')

a = Analysis(
    [os.path.join(project_root, 'invoice_macos_dialog.py')],
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
    ],
    hookspath=[os.path.join(pack_dir, 'hooks')],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='发票提取器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='发票提取器',
)

# macOS app bundle
icon_path = os.path.join(pack_dir, 'resources', 'icons', 'app.icns')
plist_path = os.path.join(pack_dir, 'resources', 'Info.plist')

app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='发票提取器.app',
    icon=icon_path if os.path.exists(icon_path) else None,
    bundle_identifier='com.fapiaoshibie.invoiceextractor',
    info_plist=plist_path if os.path.exists(plist_path) else None,
)
