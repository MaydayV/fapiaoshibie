#!/bin/bash
# 发票识别工具 - macOS启动（智能选择Python版本）

cd "$(dirname "$0")"

# 查找可用的 Python3（按优先级）
PYTHON_CANDIDATES=("/usr/bin/python3" "/usr/local/bin/python3" "python3" "python3.11" "python3.12" "python3.13")
PYTHON_FOUND=""

# 检查 Python 是否安装
for python_cmd in "${PYTHON_CANDIDATES[@]}"; do
    if command -v "$python_cmd" &> /dev/null; then
        PYTHON_FOUND="$python_cmd"
        break
    fi
done

if [ -z "$PYTHON_FOUND" ]; then
    osascript << 'DIALOG'
tell application "System Events"
    set pythonDialog to display dialog "未检测到 Python，需要先安装 Python 才能使用本工具。" & return & return & "请选择以下方式之一安装：" & return & return & "1. 访问官网下载安装" & tab & "(推荐)" & return & "2. 查看详细安装教程" buttons {"查看教程", "下载 Python", "退出"} default button 2 icon note
    set buttonResult to button returned of pythonDialog
    
    if buttonResult is "下载 Python" then
        open location "https://www.python.org/downloads/"
    else if buttonResult is "查看教程" then
        open location "https://github.com/MaydayV/fapiaoshibie/blob/main/INSTALL.md"
    end if
end tell
DIALOG
    exit 1
fi

# 检查Python版本
PYTHON_VERSION=$($PYTHON_FOUND --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)

if [ "$PYTHON_MAJOR" -lt 3 ]; then
    osascript -e 'display dialog "Python 版本过低（需要 3.7+）\\n\\n当前版本: '"$PYTHON_VERSION"'\\n\\n请升级 Python" buttons {"OK"}' > /dev/null
    exit 1
fi

# 检测 tkinter 支持
$PYTHON_FOUND -c "import tkinter" 2>/dev/null
HAS_TKINTER=$?

if [ $HAS_TKINTER -ne 0 ]; then
    osascript << 'DIALOG'
tell application "System Events"
    set tkDialog to display dialog "当前 Python 不支持图形界面（tkinter）。" & return & return & "请选择：" & return & return & "1. 使用命令行模式继续" & return & "2. 安装 tkinter 支持" buttons {"命令行模式", "安装教程", "退出"} default button 1 icon note
    set buttonResult to button returned of tkDialog
    
    if buttonResult is "安装教程" then
        open location "https://github.com/MaydayV/fapiaoshibie/blob/main/INSTALL.md#图形界面问题"
    end if
end tell
DIALOG
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

# 运行启动器
python run.py
