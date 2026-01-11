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

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 首次运行，正在创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境并安装依赖
echo 激活虚拟环境...
call venv\Scripts\activate.bat
echo 检查并安装依赖...
pip install PyMuPDF openpyxl -q >nul 2>&1

echo.
echo ========================================
echo        发票识别脚本
echo ========================================
echo.

REM 运行脚本
python invoice_extractor.py

echo.
echo 按任意键关闭...
pause >nul
