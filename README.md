# 发票识别工具 (Invoice Extractor)

自动识别和提取PDF发票信息，生成Excel清单。

## 功能特点

- 🖥️ **智能启动** - 自动检测图形界面支持，无GUI则使用命令行
- 📊 **自动提取信息** - 发票号码、日期、购买方、销售方、金额等
- 🎯 **高识别率** - PDF发票识别率接近100%
- 🔒 **虚拟环境隔离** - 不影响系统Python环境

## 快速开始

### 双击运行

#### macOS
双击 `run_macos.command` 文件

#### Windows
双击 `run_windows.bat` 文件

程序会自动：
1. 创建虚拟环境
2. 安装所需依赖
3. 检测是否支持图形界面
4. 启动对应模式（GUI或命令行）

## 运行模式

### 图形界面模式
当你的Python支持tkinter时自动启动，提供：
- 文件夹浏览选择
- 实时日志显示
- 进度提示

### 命令行模式
当tkinter不可用时自动回退，交互式输入：
- 发票目录路径
- 购买方关键词

## 关于图形界面

如果系统提示"未检测到图形界面"，说明你的Python不支持tkinter：

**macOS解决方案：**
- 使用系统自带Python (`/usr/bin/python3`)
- 或安装 `python-tk`: `brew install python-tk`

**Windows用户：**
- 通常默认支持tkinter，直接运行即可

## 系统要求

- Python 3.7+
- macOS / Windows / Linux

## 文件说明

| 文件 | 说明 |
|------|------|
| `run_macos.command` | macOS双击启动 |
| `run_windows.bat` | Windows双击启动 |
| `run.py` | 智能启动器（自动检测模式）|
| `invoice_gui.py` | 图形界面程序 |
| `invoice_extractor.py` | 命令行程序 |
| `venv/` | 虚拟环境（自动创建）|

## 识别率

- PDF发票销售方识别率: ~100%
- PDF发票金额识别率: ~100%

## License

MIT
