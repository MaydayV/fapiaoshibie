#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票识别工具 - macOS 原生对话框版本
使用 osascript 实现交互，无需 tkinter
"""

import sys
import os
import subprocess
import importlib.util

def osascript_dialog(text, buttons, default_button=1):
    """显示 macOS 原生对话框，返回用户点击的按钮"""
    button_list = buttons.split(',')
    button_script = ','.join([f'"{b}"' for b in button_list])
    
    script = f'''
    tell application "System Events"
        set dialogResult to display dialog "{text}" buttons {{{button_script}}} default button {default_button}
        return button returned of dialogResult
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def osascript_input_dialog(text, default_answer=""):
    """显示输入对话框"""
    script = f'''
    tell application "System Events"
        set dialogResult to display dialog "{text}" default answer "{default_answer}" buttons {{"确定", "取消"}} default button 1
        return text returned of dialogResult
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None

def osascript_choose_folder(prompt="选择文件夹:"):
    """显示文件夹选择对话框"""
    script = f'''
    tell application "System Events"
        set dialogResult to choose folder with prompt "{prompt}"
        return POSIX path of dialogResult
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def osascript_choose_file(prompt="选择文件", default_name=""):
    """显示文件保存对话框"""
    script = f'''
    tell application "System Events"
        set dialogResult to (choose file name with prompt "{prompt}" default name "{default_name}")
        return POSIX path of dialogResult
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def main():
    print("="*50)
    print("       发票识别工具")
    print("="*50)
    
    # 检查依赖
    try:
        import fitz
        import openpyxl
    except ImportError:
        print("正在安装依赖...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'PyMuPDF', 'openpyxl'])
        print("依赖安装完成！")
    
    # 步骤1：选择发票目录
    base_path = osascript_choose_folder("请选择发票所在目录:")

    if not base_path:
        # 如果用户取消，使用命令行输入
        base_path = input("请输入发票文件所在目录路径: ").strip()

    # 清理路径：展开 ~ 目录并处理可能的 shell 转义
    base_path = os.path.expanduser(base_path).replace('\\ ', ' ')

    if not base_path:
        print("未选择目录，程序退出")
        return
    
    # 步骤2：输入购买方关键词
    buyer_keyword = osascript_input_dialog("请输入购买方公司名称关键词:")
    
    if buyer_keyword is None:
        buyer_keyword = input("请输入购买方公司名称关键词: ").strip()
    
    if not buyer_keyword:
        print("未输入关键词，程序退出")
        return
    
    # 步骤3：选择输出文件（可选）
    output_path = osascript_choose_file("选择Excel保存位置", "发票清单.xlsx")
    
    if not output_path:
        output_path = os.path.join(base_path, "发票清单.xlsx")
    
    # 显示确认信息
    confirm = osascript_dialog(
        f"请确认：\\n\\n发票目录: {base_path}\\n购买方关键词: {buyer_keyword}\\n输出文件: {output_path}\\n\\n开始处理？",
        "开始处理,取消",
        1
    )
    
    if confirm != "开始处理":
        print("已取消")
        return
    
    # 执行处理
    print()
    print("-"*50)
    print(f"发票目录: {base_path}")
    print(f"购买方关键词: {buyer_keyword}")
    print(f"输出文件: {output_path}")
    print("-"*50)
    print()
    
    # 导入并运行主程序
    spec = importlib.util.spec_from_file_location("invoice_extractor", "invoice_extractor.py")
    extractor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extractor)
    
    extractor.process_invoices(base_path, buyer_keyword, output_path)
    
    # 完成提示
    osascript_dialog(f"处理完成！\\n\\n输出文件已保存到:\\n{output_path}", "确定")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n程序已取消")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
