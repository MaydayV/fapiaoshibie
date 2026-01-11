@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo        发票识别工具
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 未找到 Python，请先安装 Python
    echo.
    echo 访问 https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM 创建虚拟环境
if not exist "venv" (
    echo 首次运行，正在创建虚拟环境...
    python -m venv venv
    echo.
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo 检查依赖...
pip install PyMuPDF openpyxl -q >nul 2>&1

REM 用户选择
echo 请选择交互方式：
echo   1. 图形化界面（推荐）
echo   2. 命令行模式
echo.
set /p CHOICE="请输入选择 (1/2): "

if "%CHOICE%"=="1" (
    echo.
    echo 启动图形化界面...
    echo.
    python invoice_gui.py
) else if "%CHOICE%"=="2" (
    echo.
    echo 启动命令行模式...
    echo.
    python invoice_extractor.py
) else (
    echo 无效选择
)

echo.
pause
