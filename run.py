#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能启动器 - 自动检测是否支持图形界面
"""

import sys
import os

def check_tkinter():
    """检查tkinter是否可用"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def main():
    print("="*50)
    print("       发票识别工具")
    print("="*50)
    print()

    # 检查依赖
    try:
        import fitz
        import openpyxl
    except ImportError as e:
        print("正在安装依赖...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'PyMuPDF', 'openpyxl'])
        print("依赖安装完成！")
        print()

    # 尝试启动图形界面
    if check_tkinter():
        print("检测到图形界面支持，启动GUI...")
        print()
        # 导入并运行GUI
        import importlib.util
        spec = importlib.util.spec_from_file_location("invoice_gui", "invoice_gui.py")
        gui = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gui)
        gui.main()
    else:
        print("未检测到图形界面支持，使用命令行模式")
        print("提示: 如果需要图形界面，请使用系统自带Python或安装python-tk")
        print()
        print("-"*50)
        print()

        # 运行命令行版本
        import importlib.util
        spec = importlib.util.spec_from_file_location("invoice_extractor", "invoice_extractor.py")
        extractor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(extractor)

        # 交互式输入
        BASE_DIR = input("请输入发票文件所在目录路径: ").strip()
        BUYER_KEYWORD = input("请输入购买方公司名称关键词: ").strip()

        if not BASE_DIR:
            print("错误: 请输入发票目录")
            return

        OUTPUT_FILE = os.path.join(BASE_DIR, '发票清单.xlsx')

        print()
        print("-"*50)
        print(f"发票目录: {BASE_DIR}")
        print(f"购买方关键词: {BUYER_KEYWORD}")
        print(f"输出文件: {OUTPUT_FILE}")
        print("-"*50)
        print()

        extractor.process_invoices(BASE_DIR, BUYER_KEYWORD, OUTPUT_FILE)

        print()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
