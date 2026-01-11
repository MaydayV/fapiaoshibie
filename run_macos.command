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

# 用户选择运行模式
MODE=$(osascript << 'APPLESCRIPT' 2>/dev/null
tell application "System Events"
    set dialogResult to display dialog "请选择运行模式：" & return & return & "• 原生对话框 - macOS 原生交互（推荐）" & return & "• tkinter 图形界面 - 可视化窗口" & return & "• 命令行模式 - 终端交互" buttons {"原生对话框", "图形界面", "命令行模式", "退出"} default button 1
    return button returned of dialogResult
end tell
APPLESCRIPT
)

case "$MODE" in
    "原生对话框")
        exec $PYTHON_FOUND invoice_macos_dialog.py
        ;;
    "图形界面")
        exec $PYTHON_FOUND invoice_gui.py
        ;;
    "命令行模式")
        exec $PYTHON_FOUND invoice_extractor.py
        ;;
    *)
        exit 0
        ;;
esac
