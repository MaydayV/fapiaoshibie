#!/bin/bash
cd "$(dirname "$0")"

echo "========================================"
echo "       发票识别工具"
echo "========================================"
echo ""

# 查找 Python
PYTHON_FOUND=""
for py in /usr/bin/python3 /usr/local/bin/python3 python3; do
    if command -v "$py" &> /dev/null; then
        PPATH=$(command -v "$py" 2>/dev/null || echo "$py")
        if [[ "$PPATH" != *"Xcode.app"* ]]; then
            PYTHON_FOUND="$py"
            break
        fi
    fi
done

if [ -z "$PYTHON_FOUND" ]; then
    echo "未找到 Python，请先安装 Python"
    echo "访问 https://www.python.org/downloads/"
    open "https://www.python.org/downloads/"
    read -p "按回车键退出..."
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "首次运行，正在创建虚拟环境..."
    $PYTHON_FOUND -m venv venv
fi

source venv/bin/activate
# 使用虚拟环境的pip，避免调用系统pip
venv/bin/pip install PyMuPDF openpyxl -q 2>/dev/null

# 终端内选择交互方式
echo "请选择交互方式："
echo "  1. 图形化交互（使用 macOS 原生对话框）"
echo "  2. 终端交互（在终端中输入）"
echo ""
read -p "请输入选择 (1/2): " CHOICE

case "$CHOICE" in
    1)
        echo ""
        echo "启动图形化交互模式..."
        echo ""
        exec $PYTHON_FOUND invoice_macos_dialog.py
        ;;
    2)
        echo ""
        echo "启动终端交互模式..."
        echo ""
        exec $PYTHON_FOUND invoice_extractor.py
        ;;
    *)
        echo "无效选择，退出"
        exit 1
        ;;
esac
