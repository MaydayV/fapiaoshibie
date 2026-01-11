#!/bin/bash
# 发票识别工具 - macOS启动

cd "$(dirname "$0")"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    # 没有安装 Python，显示引导对话框
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

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

# 检查版本是否满足要求（Python 3.7+）
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    osascript -e 'display dialog "Python 版本过低（需要 3.7+）\\n\\n当前版本: '"$PYTHON_VERSION"'\\n\\n请升级 Python" buttons {"OK"}' > /dev/null
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "首次运行，正在创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install PyMuPDF openpyxl -q 2>/dev/null

# 运行智能启动器
python run.py
