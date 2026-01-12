"""
PyInstaller hook for invoice_extractor module
处理隐式依赖，确保 fitz 和 openpyxl 正确打包
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 隐藏导入
hiddenimports = [
    'fitz',
    'fitz.fitz',
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.styles',
    'openpyxl.utils',
    'importlib',
    'importlib.util',
]

# 收集数据文件
datas = []

# PyMuPDF 可能需要的数据文件
try:
    datas += collect_data_files('fitz', include_py_files=False)
except Exception:
    pass

# openpyxl 数据文件
try:
    datas += collect_data_files('openpyxl', include_py_files=False)
except Exception:
    pass
