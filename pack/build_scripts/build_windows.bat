@echo off
REM ===================================================================
REM 发票识别工具 - Windows 打包脚本
REM ===================================================================

chcp 65001 >nul
setlocal enabledelayedexpansion

REM 切换到脚本所在目录的父目录
cd /d "%~dp0.."

set PACK_DIR=%cd%
set PROJECT_DIR=%PACK_DIR%\..

echo ========================================
echo    发票识别工具 - Windows 打包工具
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

echo 使用 Python:
python --version
echo.

REM 检查 PyInstaller
echo 检查 PyInstaller...
python -c "import PyInstaller" 2>nul || (
    echo 正在安装 PyInstaller...
    python -m pip install pyinstaller
)

REM 检查项目依赖
echo 检查项目依赖...
python -c "import fitz" 2>nul || (
    echo 警告: PyMuPDF 未安装，正在安装...
    python -m pip install PyMuPDF
)

python -c "import openpyxl" 2>nul || (
    echo 警告: openpyxl 未安装，正在安装...
    python -m pip install openpyxl
)

echo.

REM 创建输出目录
if not exist "%PACK_DIR%\output\windows" mkdir "%PACK_DIR%\output\windows"

REM 清理旧的构建
echo 清理旧的构建文件...
if exist "%PACK_DIR%\build" rmdir /s /q "%PACK_DIR%\build"
if exist "%PACK_DIR%\dist" rmdir /s /q "%PACK_DIR%\dist"

REM 切换到项目目录进行打包
cd /d "%PROJECT_DIR%"

REM 使用 spec 文件构建
echo 开始打包 Windows exe...
pyinstaller --clean "%PACK_DIR%\config\pyinstaller_windows.spec" --workpath="%PACK_DIR%\build\win" --distpath="%PACK_DIR%\output\windows"

if exist "%PACK_DIR%\output\windows\发票识别工具.exe" (
    echo.
    echo ========================================
    echo    打包完成！
    echo ========================================
    echo.
    echo 输出位置: %PACK_DIR%\output\windows\发票识别工具.exe

    REM 显示文件大小
    for %%F in ("%PACK_DIR%\output\windows\发票识别工具.exe") do (
        set SIZE=%%~zF
        set /a SIZE_MB=!SIZE! / 1048576
        echo 文件大小: !SIZE_MB! MB
    )
) else (
    echo.
    echo ========================================
    echo    构建失败！
    echo ========================================
    echo.
    echo 请检查错误信息并重试
)

echo.
pause
