#!/bin/bash
# 发票识别工具 - macOS启动（手动选择模式）

cd "$(dirname "$0")"

# 查找 Python（排除 Xcode 版本）
PYTHON_CANDIDATES=("/usr/bin/python3" "/usr/local/bin/python3" "python3" "python3.11" "python3.12" "python3.13")
PYTHON_FOUND=""

for python_cmd in "${PYTHON_CANDIDATES[@]}"; do
    if command -v "$python_cmd" &> /dev/null; then
        PYTHON_PATH=$(command -v "$python_cmd" 2>/dev/null)
        if [[ "$PYTHON_PATH" != *"Xcode.app"* ]]; then
            PYTHON_FOUND="$python_cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_FOUND" ]; then
    osascript -e 'display dialog "未找到 Python，请先安装 Python" buttons {"OK"}' &>/dev/null
    open "https://www.python.org/downloads/"
    exit 1
fi

# 让用户选择运行模式
MODE=$(osascript << 'DIALOG'
tell application "System Events"
    set modeDialog to display dialog "请选择运行模式：" & return & return & "• 图形界面模式 - 可视化操作（需要 tkinter 支持）" & return & "• 命令行模式 - 终端交互（更稳定）" & return & return & "推荐：命令行模式更稳定，功能完全相同" buttons {"命令行模式", "图形界面", "退出"} default button 1 icon note
    set buttonResult to button returned of modeDialog
    
    if buttonResult is "命令行模式" then
        return "cli"
    else if buttonResult is "图形界面" then
        return "gui"
    else
        return "exit"
    end if
end tell
DIALOG
)

if [ "$MODE" = "exit" ]; then
    exit 0
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "首次运行，正在创建虚拟环境..."
    $PYTHON_FOUND -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install PyMuPDF openpyxl -q 2>/dev/null

# 根据用户选择运行
if [ "$MODE" = "cli" ]; then
    # 命令行模式 - 直接传递参数
    exec $PYTHON_FOUND invoice_extractor.py
else
    # 图形界面模式
    exec $PYTHON_FOUND invoice_gui.py
fi
