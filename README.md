# 发票识别工具 (Invoice Extractor)

自动识别和提取PDF发票信息，生成Excel清单。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 功能特点

- 🖥️ **智能启动** - 自动检测图形界面支持，无GUI则使用命令行
- 📊 **自动提取信息** - 发票号码、日期、购买方、销售方、金额等
- 🎯 **高识别率** - PDF发票识别率接近100%
- 🔒 **虚拟环境隔离** - 不影响系统Python环境
- 🔧 **友好引导** - 未安装Python时提供安装指引

## 快速开始

### 前置要求

- Python 3.7 或更高版本

> 💡 **没有安装 Python？**  
> 双击启动脚本时会自动检测并提供安装引导，或访问 [安装教程](INSTALL.md)

### 运行工具

#### macOS
双击 `run_macos.command` 文件

#### Windows  
双击 `run_windows.bat` 文件

### 运行模式

程序会自动：
1. 检测 Python 是否安装
2. 创建虚拟环境
3. 安装所需依赖
4. 检测图形界面支持
5. 启动对应模式

## 文件说明

| 文件 | 说明 |
|------|------|
| `run_macos.command` | macOS双击启动 |
| `run_windows.bat` | Windows双击启动 |
| `run.py` | 智能启动器 |
| `invoice_gui.py` | 图形界面程序 |
| `invoice_extractor.py` | 命令行程序 |
| `INSTALL.md` | 详细安装教程 |
| `venv/` | 虚拟环境（自动创建）|

## 安装 Python

如果需要手动安装 Python，请参考：

- 📘 [详细安装教程](INSTALL.md)
- 🔗 [Python 官网下载](https://www.python.org/downloads/)

## 常见问题

### Q: 提示"未检测到 Python"
**A**: 请先安装 Python 3.7+，双击启动脚本会提供安装引导。

### Q: 图形界面无法启动
**A**: 你的 Python 不支持 tkinter。程序会自动切换到命令行模式。

### Q: macOS 图形界面问题
**A**: 使用系统自带 Python 或通过官方安装包安装的版本通常支持GUI。

## 识别率

- PDF发票销售方识别率: ~100%
- PDF发票金额识别率: ~100%

## License

MIT

---

**GitHub**: https://github.com/MaydayV/fapiaoshibie
