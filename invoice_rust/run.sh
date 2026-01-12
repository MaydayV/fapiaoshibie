#!/bin/bash
# 发票识别工具 - Rust版本运行脚本

cd "$(dirname "$0")"

echo "=========================================="
echo "       发票识别工具 (Rust版本)"
echo "=========================================="
echo ""

# 检查Rust是否安装
if ! command -v cargo &> /dev/null; then
    echo "错误: 未找到Rust，请先安装Rust"
    echo "安装地址: https://rustup.rs/"
    exit 1
fi

# 检查是否已编译
if [ ! -f "target/release/invoice-extractor" ]; then
    echo "正在编译项目..."
    cargo build --release
    if [ $? -ne 0 ]; then
        echo "编译失败，请检查错误信息"
        exit 1
    fi
    echo "编译完成！"
    echo ""
fi

# 运行程序
echo "启动程序..."
echo ""
./target/release/invoice-extractor
