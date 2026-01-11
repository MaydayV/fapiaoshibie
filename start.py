#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票识别脚本启动器
自动检查依赖并运行主程序
"""

import sys
import subprocess
import os

def check_and_install_deps():
    """检查并安装依赖"""
    required = {'PyMuPDF', 'openpyxl'}
    missing = set()

    for package in required:
        try:
            __import__(package.replace('-', '_').lower())
        except ImportError:
            missing.add(package)

    if missing:
        print(f"正在安装依赖: {', '.join(missing)}")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-q'
        ] + list(missing))
        print("依赖安装完成！\n")

if __name__ == '__main__':
    check_and_install_deps()
    
    # 导入并运行主程序
    os.system(f'"{sys.executable}" invoice_extractor.py')
