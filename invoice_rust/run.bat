@echo off
REM 发票识别工具 - Rust版本运行脚本 (Windows)

cd /d "%~dp0"

echo ==========================================
echo        发票识别工具 (Rust版本)
echo ==========================================
echo.

REM 检查Rust是否安装
where cargo >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Rust，请先安装Rust
    echo 安装地址: https://rustup.rs/
    pause
    exit /b 1
)

REM 检查是否已编译
if not exist "target\release\invoice-extractor.exe" (
    echo 正在编译项目...
    cargo build --release
    if %errorlevel% neq 0 (
        echo 编译失败，请检查错误信息
        pause
        exit /b 1
    )
    echo 编译完成！
    echo.
)

REM 运行程序
echo 启动程序...
echo.
target\release\invoice-extractor.exe

pause
