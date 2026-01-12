# 发票提取器 - 打包说明

本目录包含将发票识别工具打包成可执行文件的所有配置和脚本。

## 打包结果

| 平台 | 输出文件 | 位置 |
|------|---------|------|
| macOS | 发票提取器.dmg | `output/macos/` |
| Windows | 发票提取器.exe | `output/windows/` |

## 使用方法

### macOS 打包

```bash
cd pack/build_scripts
./build_macos.sh
```

输出文件：
- `output/macos/发票提取器.app` - macOS 应用程序
- `output/macos/发票提取器.dmg` - macOS 磁盘映像（分发用）

### Windows 打包

在 Windows 系统上：

```cmd
cd pack\build_scripts
build_windows.bat
```

输出文件：
- `output/windows/发票提取器.exe` - Windows 单文件可执行程序

## 目录结构

```
pack/
├── README.md                   # 本文档
├── requirements-pack.txt       # 打包工具依赖
│
├── config/                     # PyInstaller 配置
│   ├── pyinstaller_macos.spec  # macOS 配置
│   └── pyinstaller_windows.spec# Windows 配置
│
├── hooks/                      # PyInstaller 钩子
│   └── hook-invoice_extractor.py
│
├── build_scripts/              # 构建脚本
│   ├── build_macos.sh          # macOS 构建脚本
│   └── build_windows.bat       # Windows 构建脚本
│
├── resources/                  # 资源文件
│   ├── Info.plist             # macOS app 配置
│   └── icons/                 # 应用图标
│       ├── app.icns           # macOS 图标
│       └── app.ico            # Windows 图标
│
└── output/                     # 打包输出
    ├── macos/
    └── windows/
```

## 依赖要求

打包前需要安装：

1. Python 3.8+
2. PyInstaller: `pip install pyinstaller`
3. 项目依赖: PyMuPDF, openpyxl

## 注意事项

1. **图标文件**: 将自定义图标放在 `resources/icons/` 目录
   - macOS: `app.icns` (推荐尺寸 1024x1024)
   - Windows: `app.ico` (推荐尺寸 256x256)

2. **首次运行**: 打包脚本会自动安装 PyInstaller

3. **文件大小**:
   - macOS .app: ~68MB
   - macOS .dmg: ~32MB (压缩后)
   - Windows .exe: ~40-60MB (单文件)

4. **代码签名**:
   - macOS 打包后可能需要签名才能在其他 Mac 上运行
   - Windows 可执行文件可能被杀软误报

## 测试打包结果

### macOS
```bash
# 直接运行 app
open output/macos/发票提取器.app

# 或安装 dmg
open output/macos/发票提取器.dmg
```

### Windows
双击 `发票提取器.exe` 运行
