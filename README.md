# 发票识别脚本 (Invoice Extractor)

自动识别和提取PDF发票信息，生成Excel清单。

## 功能特点

- 自动扫描目录中的所有PDF发票文件
- 提取发票号码、开票日期、购买方、销售方、金额等信息
- 支持多种销售方类型（有限公司、个体工商户、商行等）
- 从图片文件名中提取金额（订单截图等）
- 生成格式化的Excel清单
- **使用虚拟环境隔离依赖，不影响系统Python环境**

## 快速开始（双击运行）

### macOS
双击 `run_macos.command` 文件即可运行

### Windows
双击 `run_windows.bat` 文件即可运行

首次运行会自动创建虚拟环境并安装依赖。

## 高级用法（命令行）

```bash
# 方式1：交互式运行
python invoice_extractor.py

# 方式2：使用虚拟环境运行
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

python invoice_extractor.py <发票目录> <购买方关键词> [输出文件]
```

## 系统要求

- Python 3.7+
- macOS / Windows / Linux

## 文件说明

| 文件 | 说明 |
|------|------|
| `run_macos.command` | macOS双击启动文件 |
| `run_windows.bat` | Windows双击启动文件 |
| `invoice_extractor.py` | 主程序 |
| `venv/` | 虚拟环境（首次运行自动创建）|

## 识别率

- PDF发票销售方识别率: ~100%
- PDF发票金额识别率: ~100%
- 整体金额识别率: ~99.5%

## 提取字段

| 字段 | 说明 |
|------|------|
| 序号 | 自动编号 |
| 文件夹 | 发票所在的文件夹路径 |
| 文件名 | 发票文件名 |
| 发票号码 | 20位发票号码 |
| 开票日期 | YYYY-MM-DD格式 |
| 购买方 | 购买方公司名称 |
| 购买方税号 | 购买方统一社会信用代码 |
| 销售方 | 销售方公司名称 |
| 销售方税号 | 销售方统一社会信用代码 |
| 项目内容 | 发票项目内容 |
| 金额 | 价税合计金额 |

## License

MIT
