# 图标文件说明

请将自定义图标放置在此目录：

## macOS 图标
- **文件名**: `app.icns`
- **推荐尺寸**: 1024x1024 像素
- **格式**: macOS 图标容器格式

## Windows 图标
- **文件名**: `app.ico`
- **推荐尺寸**: 256x256 像素
- **格式**: Windows 图标格式

## 如何创建图标文件

### 从 PNG 创建 ICNS (macOS)
```bash
# 使用在线工具或命令行工具
# 在线工具: https://cloudconvert.com/png-to-icns
# 或使用 iconutil (macOS 自带)
mkdir AppIcon.iconset
sips -z 16 16     icon.png --out AppIcon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out AppIcon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out AppIcon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out AppIcon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out AppIcon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out AppIcon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out AppIcon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out AppIcon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out AppIcon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out AppIcon.iconset/icon_512x512@2x.png
iconutil -c icns AppIcon.iconset
```

### 从 PNG 创建 ICO (Windows)
- 在线工具: https://cloudconvert.com/png-to-ico
- 或使用 GIMP、Photoshop 等图像编辑软件

## 注意事项

如果没有提供自定义图标，构建过程会使用 PyInstaller 的默认图标，程序仍可正常运行。
