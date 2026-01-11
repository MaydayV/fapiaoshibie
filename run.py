#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能启动器 - 自动检测是否支持图形界面
"""

import sys
import os
import traceback
import subprocess

def check_tkinter():
    """检查tkinter是否真正可用"""
    try:
        import tkinter
        # 尝试创建一个测试窗口
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:
        return False

def suggest_tkinter_install():
    """提供tkinter安装建议"""
    print("提示：图形界面需要 tkinter 支持")
    print()
    print("解决方案：")
    print("  1. 使用系统自带 Python（通常已支持）")
    print("     系统路径: /usr/bin/python3")
    print()
    print("  2. 如果使用 Homebrew Python，安装 python-tk：")
    print("     brew install python-tk")
    print()
    print("  3. 使用 Python 官网安装包重新安装")
    print("     下载地址: https://www.python.org/downloads/")
    print()
    print("现在将使用命令行模式...")
    print()

def main():
    print("="*50)
    print("       发票识别工具")
    print("="*50)
    print()

    # 检查依赖
    try:
        import fitz
        import openpyxl
    except ImportError:
        print("正在安装依赖...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'PyMuPDF', 'openpyxl'])
        print("依赖安装完成！")
        print()

    # 检查tkinter
    gui_available = check_tkinter()

    # 尝试启动图形界面
    if gui_available:
        print("检测到图形界面支持，启动GUI...")
        print()
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("invoice_gui", "invoice_gui.py")
            gui = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gui)
            gui.main()
            return
        except Exception as e:
            print(f"图形界面启动失败: {e}")
            print()
            suggest_tkinter_install()

    # 命令行模式
    print("="*50)
    print("       命令行模式")
    print("="*50)
    print()

    # 导入主程序
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

    try:
        extractor.process_invoices(BASE_DIR, BUYER_KEYWORD, OUTPUT_FILE)
    except Exception as e:
        print(f"处理失败: {e}")
        traceback.print_exc()

    print()
    input("按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已取消")
    except Exception as e:
        print(f"\n程序异常: {e}")
        traceback.print_exc()
        input("按回车键退出...")
