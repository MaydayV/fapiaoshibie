@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 用户选择运行模式
echo ========================================
echo        发票识别工具
echo ========================================
echo.
echo 请选择运行模式：
echo.
echo   1. 命令行模式（推荐，更稳定）
echo   2. 图形界面模式
echo   3. 退出
echo.
choice /c 123 /n /m "请选择 (1-3): "

if errorlevel 3 (
    exit /b 0
) else if errorlevel 2 (
    goto GUI_MODE
) else if errorlevel 1 (
    goto CLI_MODE
)

:CLI_MODE
echo.
echo 启动命令行模式...
echo.

REM 创建虚拟环境
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install PyMuPDF openpyxl -q >nul 2>&1

python invoice_extractor.py
pause
exit /b 0

:GUI_MODE
echo.
echo 启动图形界面模式...
echo.

REM 创建虚拟环境
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install PyMuPDF openpyxl -q >nul 2>&1

python invoice_gui.py
pause
exit /b 0
