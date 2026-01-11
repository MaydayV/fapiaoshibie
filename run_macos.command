#!/bin/bash
# 发票识别脚本 - macOS双击启动版（使用虚拟环境）

cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "未找到 Python3，请先安装 Python" buttons {"OK"}'
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "首次运行，正在创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "激活虚拟环境..."
source venv/bin/activate
echo "检查并安装依赖..."
pip install PyMuPDF openpyxl -q

echo ""
echo "========================================"
echo "       发票识别脚本"
echo "========================================"
echo ""

# 运行脚本
python invoice_extractor.py

echo ""
echo "按任意键关闭窗口..."
read -n 1
