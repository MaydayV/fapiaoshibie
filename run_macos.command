#!/bin/bash
# 发票识别工具 - macOS启动（跳过Xcode Python）

cd "$(dirname "$0")"

# 查找可用的 Python3（排除Xcode版本）
PYTHON_CANDIDATES=("/usr/bin/python3" "/usr/local/bin/python3" "python3" "python3.11" "python3.12" "python3.13")
PYTHON_FOUND=""

echo "正在查找 Python..."
for python_cmd in "${PYTHON_CANDIDATES[@]}"; do
    if command -v "$python_cmd" &> /dev/null; then
        # 检查是否是 Xcode 的 Python（跳过）
        PYTHON_PATH=$(command -v "$python_cmd" 2>/dev/null)
        if [[ "$PYTHON_PATH" != *"Xcode.app"* ]]; then
            PYTHON_FOUND="$python_cmd"
            PYTHON_VERSION=$($PYTHON_FOUND --version 2>&1)
            echo "  找到: $PYTHON_FOUND ($PYTHON_VERSION)"
            break
        else
            echo "  跳过 Xcode Python: $PYTHON_PATH"
        fi
    fi
done

# 如果只找到 Xcode Python，提示用户
if [ -z "$PYTHON_FOUND" ]; then
    osascript << 'DIALOG'
tell application "System Events"
    set pythonDialog to display dialog "未找到合适的 Python 版本。" & return & return & return & "Xcode 自带的 Python 与 tkinter 不兼容。" & return & return & "请选择以下方式之一：" & return & return & "1. 使用命令行模式（推荐）" & return & "2. 从官网安装 Python" & return & "3. 查看详细教程" buttons {"命令行模式", "安装教程", "退出"} default button 1 icon note
    set buttonResult to button returned of pythonDialog
    
    if buttonResult is "安装教程" then
        open location "https://github.com/MaydayV/fapiaoshibie/blob/main/INSTALL.md"
    else if buttonResult is "退出" then
        -- 退出
    end if
end tell
DIALOG
    
    # 如果用户选择命令行模式，继续
    if [ "$?" -ne 0 ]; then
        exit 1
    fi
fi

# 检查Python版本
if [ -n "$PYTHON_FOUND" ]; then
    PYTHON_VERSION=$($PYTHON_FOUND --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    
    if [ "$PYTHON_MAJOR" -lt 3 ]; then
        osascript -e 'display dialog "Python 版本过低（需要 3.7+）" buttons {"OK"}'
        exit 1
    fi
else
    # 没找到合适的Python，使用系统python3作为后备
    PYTHON_FOUND="python3"
fi

# 检测 tkinter 支持
$PYTHON_FOUND -c "import tkinter; root = tkinter.Tk(); root.destroy()" 2>/dev/null
HAS_TKINTER=$?

if [ $HAS_TKINTER -ne 0 ]; then
    # tkinter不可用，直接使用命令行模式
    echo ""
    echo "图形界面不可用，使用命令行模式..."
    echo ""
    USE_CLI_MODE=true
else
    echo ""
    echo "图形界面可用，启动中..."
    echo ""
    USE_CLI_MODE=false
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "首次运行，正在创建虚拟环境..."
    $PYTHON_FOUND -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "检查依赖..."
pip install PyMuPDF openpyxl -q 2>/dev/null

# 运行
if [ "$USE_CLI_MODE" = true ]; then
    # 强制命令行模式
    $PYTHON_FOUND -c "
import sys
sys.argv.insert(1, '--cli')
exec(open('run.py').read())
"
else
    $PYTHON_FOUND run.py
fi
