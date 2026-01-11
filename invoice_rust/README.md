# 发票识别工具 (Rust版本)

使用Rust编写的发票识别工具，自动识别和提取PDF发票信息，生成Excel清单。

![Rust](https://img.shields.io/badge/Rust-1.70+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 功能特点

- 🖥️ **图形化界面** - 使用egui构建的现代化GUI界面
- 📊 **自动提取信息** - 发票号码、日期、购买方、销售方、金额等
- 🎯 **高识别率** - PDF发票识别率接近100%
- ⚡ **高性能** - Rust原生性能，处理速度快
- 🔒 **内存安全** - Rust的内存安全保证

## 系统要求

- Rust 1.70 或更高版本
- macOS / Windows / Linux

## 安装和运行

### 1. 安装Rust

如果还没有安装Rust，请访问 [rustup.rs](https://rustup.rs/) 安装。

### 2. 编译项目

```bash
cd invoice_rust
cargo build --release
```

### 3. 运行程序

```bash
cargo run --release
```

或者直接运行编译后的可执行文件：

```bash
./target/release/invoice-extractor
```

## 使用方法

1. **选择发票目录** - 点击"浏览..."按钮选择包含发票PDF文件的目录
2. **输入购买方关键词** - 输入购买方公司名称的关键词（用于识别购买方）
3. **选择输出文件** - 选择Excel文件的保存位置（可选，默认为发票目录下的"发票清单.xlsx"）
4. **开始识别** - 点击"开始识别"按钮，程序会自动处理所有发票文件
5. **查看结果** - 处理完成后，在日志区域查看识别结果，Excel文件已保存到指定位置

## 识别字段

程序会自动提取以下信息：

- 发票号码（20位数字）
- 开票日期
- 购买方名称
- 购买方税号
- 销售方名称
- 销售方税号
- 项目内容
- 金额

## 技术栈

- **GUI框架**: egui + eframe
- **PDF处理**: pdf-extract
- **正则表达式**: regex
- **Excel生成**: rust_xlsxwriter
- **文件对话框**: rfd

## 项目结构

```
invoice_rust/
├── Cargo.toml          # 项目配置和依赖
├── README.md           # 项目说明文档
└── src/
    ├── main.rs         # 程序入口
    ├── extractor.rs    # 发票信息提取核心逻辑
    └── gui.rs          # GUI界面实现
```

## 核心识别方法

本项目使用基于规则的文本提取方法：

1. **PDF文本提取** - 使用pdf-extract库从PDF中提取纯文本
2. **正则表达式匹配** - 使用多个正则表达式模式识别和提取不同的发票信息字段
3. **关键词匹配** - 通过关键词识别销售方和购买方
4. **上下文分析** - 从税号附近提取公司名称

## 识别率

- PDF发票销售方识别率: ~100%
- PDF发票金额识别率: ~100%

## 与Python版本的对比

| 特性 | Python版本 | Rust版本 |
|------|-----------|---------|
| 性能 | 中等 | 高 |
| 内存占用 | 较高 | 较低 |
| 启动速度 | 较慢 | 快 |
| 跨平台 | 是 | 是 |
| GUI框架 | tkinter | egui |
| 依赖管理 | pip | Cargo |

## 开发

### 添加新功能

1. 修改 `src/extractor.rs` 添加新的提取逻辑
2. 修改 `src/gui.rs` 更新界面
3. 运行 `cargo test` 进行测试

### 构建发布版本

```bash
cargo build --release
```

可执行文件位于 `target/release/invoice-extractor`

## License

MIT

---

**GitHub**: https://github.com/MaydayV/fapiaoshibie
