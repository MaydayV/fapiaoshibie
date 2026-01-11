#!/bin/bash
# 发票识别脚本 - macOS双击启动版

cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "未找到 Python3，请先安装 Python" buttons {"OK"}'
    exit 1
fi

# 自动安装依赖
echo "正在检查依赖..."
pip3 install PyMuPDF openpyxl -q 2>/dev/null

echo ""
echo "========================================"
echo "       发票识别脚本"
echo "========================================"
echo ""

# 运行脚本
python3 invoice_extractor.py

echo ""
echo "按任意键关闭窗口..."
read -n 1
