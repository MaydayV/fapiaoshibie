#!/bin/bash
# 发票识别工具 - macOS启动

cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "未找到 Python3，请先安装 Python" buttons {"OK"}'
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate
pip install PyMuPDF openpyxl -q 2>/dev/null

# 启动图形界面
python invoice_gui.py
