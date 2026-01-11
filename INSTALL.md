# 安装教程

## 第一步：安装 Python

### macOS 用户

#### 方法一：使用官方安装包（推荐）

1. 访问 Python 官网：https://www.python.org/downloads/
2. 下载 macOS 版本的 Python 安装包
3. 双击安装包，按提示完成安装

#### 方法二：使用 Homebrew

```bash
# 如果没有 Homebrew，先安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python@3.11
```

### Windows 用户

1. 访问 Python 官网：https://www.python.org/downloads/
2. 下载 Windows 版本的 Python 安装包
3. 运行安装程序，**务必勾选 "Add Python to PATH"**
4. 点击 "Install Now" 完成安装

### Linux 用户

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-tk

# CentOS/RHEL
sudo yum install python3 python3-pip python3-tk
```

---

## 第二步：验证安装

打开终端/命令提示符，输入：

```bash
python3 --version
```

或

```bash
python --version
```

如果显示版本号（如 Python 3.11.x），说明安装成功。

---

## 第三步：运行发票识别工具

### 方法一：双击运行

- **macOS**: 双击 `run_macos.command`
- **Windows**: 双击 `run_windows.bat`

### 方法二：命令行运行

```bash
# 进入工具目录
cd fapiaoshibie

# 运行启动器
python3 run.py
```

---

## 常见问题

### Q: macOS 提示 "未找到 Python3"
**A**: 请确保使用系统自带 Python 或通过官方安装包安装。Homebrew 版本的 Python 可能需要额外配置。

### Q: Windows 提示 "python 不是内部或外部命令"
**A**: 请重新安装 Python，确保勾选 "Add Python to PATH" 选项。

### Q: 图形界面无法启动
**A**: 这是因为 Python 不支持 tkinter。
- **macOS**: 使用系统自带 Python 或安装 `python-tk`
- **Windows**: 通常默认支持，如遇问题请重新安装 Python

### Q: 虚拟环境创建失败
**A**: 确保有写入权限，或在命令行手动运行：
```bash
python3 -m venv venv
```

---

## 获取帮助

如果遇到问题，请访问：
- GitHub Issues: https://github.com/MaydayV/fapiaoshibie/issues
