#!/bin/bash
# ===================================================================
# 发票识别工具 - macOS 打包脚本
# ===================================================================

set -e

# 切换到脚本所在目录的父目录
cd "$(dirname "$0")/.."

PACK_DIR="$(pwd)"
PROJECT_DIR="$(dirname "$PACK_DIR")"

echo "========================================"
echo "   发票识别工具 - macOS 打包工具"
echo "========================================"
echo ""

# 检查 Python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

if ! command -v "$PYTHON_CMD" &> /dev/null; then
    echo "错误: 未找到 Python，请先安装 Python"
    exit 1
fi

echo "使用 Python: $($PYTHON_CMD --version)"
echo ""

# 检查 PyInstaller
echo "检查 PyInstaller..."
if ! $PYTHON_CMD -c "import PyInstaller" 2>/dev/null; then
    echo "正在安装 PyInstaller..."
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    $PYTHON_CMD -m pip install --break-system-packages pyinstaller
fi

# 检查项目依赖
echo "检查项目依赖..."
if ! $PYTHON_CMD -c "import fitz" 2>/dev/null; then
    echo "警告: PyMuPDF 未安装，正在安装..."
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    $PYTHON_CMD -m pip install --break-system-packages PyMuPDF
fi

if ! $PYTHON_CMD -c "import openpyxl" 2>/dev/null; then
    echo "警告: openpyxl 未安装，正在安装..."
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    $PYTHON_CMD -m pip install --break-system-packages openpyxl
fi

echo ""

# App 名称
APP_NAME="发票提取器"

# 创建输出目录
mkdir -p "$PACK_DIR/output/macos"

# 清理旧的构建
echo "清理旧的构建文件..."
rm -rf "$PACK_DIR/build/"
rm -rf "$PACK_DIR/dist/"
rm -rf "$PACK_DIR/output/macos/$APP_NAME"
rm -rf "$PACK_DIR/output/macos/$APP_NAME.app"
rm -f "$PACK_DIR/output/macos/$APP_NAME.dmg"

# 切换到项目目录进行打包
cd "$PROJECT_DIR"

# 使用 spec 文件构建
echo "开始打包 macOS app..."
pyinstaller --clean "$PACK_DIR/config/pyinstaller_macos.spec" \
    --workpath="$PACK_DIR/build/mac" \
    --distpath="$PACK_DIR/output/macos"

# 检查构建结果（app是目录不是文件）
if [ -d "$PACK_DIR/output/macos/$APP_NAME.app" ]; then
    echo ""
    echo "========================================"
    echo "   App 构建成功！"
    echo "========================================"
    echo ""
    echo "位置: $PACK_DIR/output/macos/$APP_NAME.app"

    # 显示文件大小
    SIZE=$(du -sh "$PACK_DIR/output/macos/$APP_NAME.app" | cut -f1)
    echo "大小: $SIZE"
    echo ""

    # 创建 DMG
    if command -v hdiutil &> /dev/null; then
        echo "正在创建 DMG..."

        DMG_PATH="$PACK_DIR/output/macos/$APP_NAME.dmg"

        # 临时目录
        TMP_DIR=$(mktemp -d)

        # 复制 app 到临时目录
        cp -R "$PACK_DIR/output/macos/$APP_NAME.app" "$TMP_DIR/"

        # 删除旧的 DMG
        rm -f "$DMG_PATH"

        # 创建 DMG
        hdiutil create -volname "$APP_NAME" \
                       -srcfolder "$TMP_DIR" \
                       -ov \
                       -format UDZO \
                       -imagekey zlib-level=9 \
                       "$DMG_PATH" > /dev/null

        # 清理
        rm -rf "$TMP_DIR"

        DMG_SIZE=$(du -sh "$DMG_PATH" | cut -f1)
        echo "DMG 创建成功: $DMG_PATH"
        echo "大小: $DMG_SIZE"
    fi

    echo ""
    echo "========================================"
    echo "   打包完成！"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "   构建失败！"
    echo "========================================"
    echo ""
    echo "请检查错误信息并重试"
    exit 1
fi
