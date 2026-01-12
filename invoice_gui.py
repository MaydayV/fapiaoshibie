#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票识别脚本 - 图形界面版本 (Windows/Linux)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import os
import sys


def check_and_install_deps():
    """检查并安装依赖"""
    required = {'PyMuPDF', 'openpyxl'}
    missing = set()

    for package in required:
        module_name = package.replace('-', '_').lower()
        try:
            __import__(module_name)
        except ImportError:
            missing.add(package)

    if missing:
        return False, f"需要安装依赖: {', '.join(missing)}"
    return True, ""


def install_deps(callback):
    """在线程中安装依赖"""
    import subprocess
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-q',
            'PyMuPDF', 'openpyxl'
        ])
        callback(True, "依赖安装完成！")
    except Exception as e:
        callback(False, f"安装失败: {str(e)}")


def process_invoices(base_path, buyer_keyword, output_path, log_callback):
    """处理发票并生成Excel"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("invoice_extractor", "invoice_extractor.py")
    extractor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extractor)
    return extractor.process_invoices(base_path, buyer_keyword, output_path, log_callback)


class InvoiceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("发票识别工具")
        self.root.geometry("550x450")
        self.root.resizable(True, True)

        # 检查依赖
        deps_ok, deps_msg = check_and_install_deps()
        self.deps_ok = deps_ok

        self.setup_ui()

        if not deps_ok:
            self.log(f"⚠️ {deps_msg}")
            self.log("请点击下方按钮安装依赖...")

    def setup_ui(self):
        # 主框架
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(main_frame, text="📄 发票识别工具",
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 15))

        # 配置区域
        config_frame = tk.LabelFrame(main_frame, text="配置选项", padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))

        # 发票目录
        tk.Label(config_frame, text="发票目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.dir_entry = tk.Entry(config_frame, width=35)
        self.dir_entry.grid(row=0, column=1, pady=5, padx=5)
        tk.Button(config_frame, text="浏览...", command=self.browse_dir,
                 width=8).grid(row=0, column=2)

        # 购买方关键词
        tk.Label(config_frame, text="购买方关键词:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.buyer_entry = tk.Entry(config_frame, width=35)
        self.buyer_entry.grid(row=1, column=1, pady=5, padx=5)

        # 输出文件
        tk.Label(config_frame, text="输出文件:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_entry = tk.Entry(config_frame, width=35)
        self.output_entry.grid(row=2, column=1, pady=5, padx=5)
        tk.Button(config_frame, text="浏览...", command=self.browse_output,
                 width=8).grid(row=2, column=2)

        # 日志区域
        log_frame = tk.LabelFrame(main_frame, text="运行日志", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=60)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 按钮区域
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        self.install_btn = tk.Button(btn_frame, text="安装依赖", bg="#f39c12", fg="white",
                                    command=self.install_deps, width=10)
        self.install_btn.pack(side=tk.LEFT, padx=(0, 10))

        if self.deps_ok:
            self.install_btn.config(state=tk.DISABLED, text="依赖已安装")

        self.run_btn = tk.Button(btn_frame, text="开始识别", bg="#27ae60", fg="white",
                                 command=self.run_extractor, font=("Arial", 10, "bold"),
                                 width=12)
        self.run_btn.pack(side=tk.RIGHT)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = tk.Label(main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def browse_dir(self):
        directory = filedialog.askdirectory(title="选择发票所在目录")
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)

    def log(self, message):
        # 同时输出到GUI和终端
        print(message)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def install_deps(self):
        def update_callback(success, msg):
            self.install_btn.config(text="依赖已安装", state=tk.DISABLED)
            self.deps_ok = True
            self.log(msg)

        self.log("正在安装依赖...")
        self.install_btn.config(state=tk.DISABLED, text="安装中...")
        thread = threading.Thread(target=lambda: install_deps(update_callback))
        thread.start()

    def run_extractor(self):
        dir_path = self.dir_entry.get().strip()
        buyer_keyword = self.buyer_entry.get().strip()
        output_path = self.output_entry.get().strip()

        # 清理路径：展开 ~ 目录并处理可能的 shell 转义
        # 注意：只在Unix-like系统上处理\ 转义，避免影响Windows网络路径
        dir_path = os.path.expanduser(dir_path)
        if os.name != 'nt':  # 非Windows系统
            dir_path = dir_path.replace('\\ ', ' ')
        if output_path:
            output_path = os.path.expanduser(output_path)
            if os.name != 'nt':  # 非Windows系统
                output_path = output_path.replace('\\ ', ' ')

        if not dir_path:
            messagebox.showwarning("提示", "请选择发票目录")
            return

        if not buyer_keyword:
            messagebox.showwarning("提示", "请输入购买方关键词")
            return

        if not output_path:
            output_path = os.path.join(dir_path, "发票清单.xlsx")
            self.output_entry.insert(0, output_path)

        self.run_btn.config(state=tk.DISABLED, text="处理中...")

        def run_thread():
            try:
                self.log("="*50)
                self.log("开始处理发票...")
                self.log(f"发票目录: {dir_path}")
                self.log(f"购买方关键词: {buyer_keyword}")
                self.log(f"输出文件: {output_path}")
                self.log("="*50)

                result = process_invoices(dir_path, buyer_keyword, output_path, self.log)

                self.root.after(0, lambda: self.complete(True, result))
            except Exception as e:
                self.root.after(0, lambda: self.complete(False, str(e)))

        thread = threading.Thread(target=run_thread)
        thread.start()

    def complete(self, success, result):
        self.run_btn.config(state=tk.NORMAL, text="开始识别")

        if success:
            self.log("="*50)
            self.log("✅ 处理完成！")
            self.log(f"📁 输出文件: {result}")
            self.log("="*50)
            self.status_var.set("处理完成")
            messagebox.showinfo("完成", f"发票识别完成！\n\n输出文件: {result}")
        else:
            self.log(f"❌ 处理失败: {result}")
            self.status_var.set("处理失败")
            messagebox.showerror("错误", f"处理失败:\n{result}")


def main():
    root = tk.Tk()
    app = InvoiceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
