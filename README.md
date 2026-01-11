# 发票识别工具 (Invoice Extractor)

自动识别和提取PDF发票信息，生成Excel清单。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 功能特点

- 🖥️ **两种交互方式** - 图形化对话框 / 终端命令行
- 📊 **自动提取信息** - 发票号码、日期、购买方、销售方、金额等
- 🎯 **高识别率** - PDF发票识别率接近100%
- 🔒 **虚拟环境隔离** - 不影响系统Python环境
- 🍎 **macOS 原生对话框** - 使用系统原生 API，稳定可靠

## 快速开始

### 运行工具

#### macOS
双击 `run_macos.command` 文件，选择交互方式：
- **图形化交互** - 使用 macOS 原生对话框（推荐）
- **终端交互** - 在终端中输入

#### Windows
双击 `run_windows.bat` 文件

## 文件说明

| 文件 | 说明 |
|------|------|
| `run_macos.command` | macOS 双击启动 |
| `run_windows.bat` | Windows 双击启动 |
| `invoice_macos_dialog.py` | macOS 原生对话框模式 |
| `invoice_extractor.py` | 终端交互模式 |
| `INSTALL.md` | 详细安装教程 |
| `venv/` | 虚拟环境（自动创建）|

## 安装 Python

如果需要手动安装 Python，请参考：

- 📘 [详细安装教程](INSTALL.md)
- 🔗 [Python 官网下载](https://www.python.org/downloads/)

## 识别率

- PDF发票销售方识别率: ~100%
- PDF发票金额识别率: ~100%

## License

MIT

---

**GitHub**: https://github.com/MaydayV/fapiaoshibie
