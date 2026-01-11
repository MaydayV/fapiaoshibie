#!/bin/bash
cd "$(dirname "$0")"

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
    osascript -e 'display dialog "未找到 Python，请先安装 Python" buttons {"OK"}' 2>/dev/null
    open "https://www.python.org/downloads/"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "首次运行，正在创建虚拟环境..."
    $PYTHON_FOUND -m venv venv
fi

source venv/bin/activate
pip install PyMuPDF openpyxl -q 2>/dev/null

# 用户选择：图形化交互 vs 终端交互
MODE=$(osascript << 'APPLESCRIPT' 2>/dev/null
tell application "System Events"
    set dialogResult to display dialog "请选择交互方式：" & return & return & "• 图形化交互 - 使用对话框选择和输入" & return & "• 终端交互 - 在终端中输入命令" buttons {"图形化交互", "终端交互", "退出"} default button 1
    return button returned of dialogResult
end tell
APPLESCRIPT
)

if [[ "$MODE" == "退出" ]] || [[ -z "$MODE" ]]; then
    exit 0
fi

if [[ "$MODE" == "图形化交互" ]]; then
    exec $PYTHON_FOUND invoice_macos_dialog.py
else
    exec $PYTHON_FOUND invoice_extractor.py
fi
