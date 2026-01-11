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

REM 创建虚拟环境
if not exist "venv" (
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat
pip install PyMuPDF openpyxl -q >nul 2>&1

REM 运行智能启动器（自动检测GUI支持）
python run.py
