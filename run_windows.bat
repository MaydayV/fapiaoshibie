@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ==========================================
    echo        未检测到 Python
    echo ==========================================
    echo.
    echo 本工具需要 Python 才能运行，请先安装 Python。
    echo.
    echo 请选择：
    echo   1. 访问官网下载 Python (推荐)
    echo   2. 查看详细安装教程
    echo   3. 退出
    echo.
    choice /c 123 /n /m "请选择 (1-3): "
    
    if errorlevel 3 (
        exit /b 0
    ) else if errorlevel 2 (
        start https://github.com/MaydayV/fapiaoshibie/blob/main/INSTALL.md
        exit /b 0
    ) else if errorlevel 1 (
        start https://www.python.org/downloads/
        exit /b 0
    )
)

REM 创建虚拟环境
if not exist "venv" (
    echo 首次运行，正在创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
pip install PyMuPDF openpyxl -q >nul 2>&1

REM 运行智能启动器
python run.py
