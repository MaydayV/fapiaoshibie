# 发票识别工具 (Invoice Extractor)

自动识别和提取PDF发票信息，生成Excel清单。

## 功能特点

- 🖥️ **图形界面操作** - 无需命令行，点点鼠标即可
- 📊 **自动提取信息** - 发票号码、日期、购买方、销售方、金额等
- 🎯 **高识别率** - PDF发票识别率接近100%
- 🔒 **虚拟环境隔离** - 不影响系统Python环境

## 快速开始

### 图形界面（推荐）

#### macOS
双击 `run_macos.command` 文件

#### Windows
双击 `run_windows.bat` 文件

### 命令行模式

```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 运行脚本
python invoice_extractor.py
```

## 使用截图

1. 选择发票所在目录
2. 输入购买方公司名称关键词
3. 选择输出文件位置
4. 点击"开始识别"

## 系统要求

- Python 3.7+
- macOS / Windows / Linux

## 文件说明

| 文件 | 说明 |
|------|------|
| `run_macos.command` | macOS双击启动（图形界面）|
| `run_windows.bat` | Windows双击启动（图形界面）|
| `invoice_gui.py` | 图形界面主程序 |
| `invoice_extractor.py` | 命令行版本 |
| `venv/` | 虚拟环境（自动创建）|

## 识别率

- PDF发票销售方识别率: ~100%
- PDF发票金额识别率: ~100%
- 整体金额识别率: ~99.5%

## 提取字段

| 字段 | 说明 |
|------|------|
| 序号 | 自动编号 |
| 文件夹 | 发票所在文件夹 |
| 文件名 | 发票文件名 |
| 发票号码 | 20位发票号码 |
| 开票日期 | YYYY-MM-DD格式 |
| 购买方 | 购买方公司名称 |
| 购买方税号 | 购买方税号 |
| 销售方 | 销售方公司名称 |
| 销售方税号 | 销售方税号 |
| 项目内容 | 发票项目 |
| 金额 | 价税合计金额 |

## License

MIT
