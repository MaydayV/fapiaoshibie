@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo        发票识别脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 自动安装依赖
echo 正在检查依赖...
pip install PyMuPDF openpyxl -q >nul 2>&1

echo.

REM 运行脚本
python invoice_extractor.py

echo.
echo 按任意键关闭...
pause >nul
