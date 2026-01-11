#!/bin/bash
cd "$(dirname "$0")"

# 查找 Python（排除 Xcode 版本）
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

# 用户选择运行模式
MODE=$(osascript << 'APPLESCRIPT' 2>/dev/null
tell application "System Events"
    set dialogResult to display dialog "请选择运行模式：" & return & return & "• 命令行模式 - 终端交互（推荐，更稳定）" & return & "• 图形界面模式 - 可视化操作" buttons {"命令行模式", "图形界面", "退出"} default button 1
    return button returned of dialogResult
end tell
APPLESCRIPT
)

# 处理用户选择（检查是否为退出）
if [[ "$MODE" == "退出" ]] || [[ -z "$MODE" ]]; then
    if [[ "$MODE" != "退出" ]]; then
        # osascript 失败，默认使用命令行模式
        MODE="命令行模式"
    else
        exit 0
    fi
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "首次运行，正在创建虚拟环境..."
    $PYTHON_FOUND -m venv venv 2>/dev/null || {
        osascript -e 'display dialog "虚拟环境创建失败" buttons {"OK"}'
        exit 1
    }
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install PyMuPDF openpyxl -q 2>/dev/null

# 根据选择运行
if [[ "$MODE" == "命令行模式"* ]]; then
    exec $PYTHON_FOUND invoice_extractor.py
else
    exec $PYTHON_FOUND invoice_gui.py
fi
