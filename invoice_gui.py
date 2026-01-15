#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票提取器 - Windows/Linux 版本
直接进入主界面
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import os
import sys
import queue

# 版本号
VERSION = "1.0.3"


def get_resource_path(relative_path):
    """获取资源文件的绝对路径（兼容 PyInstaller 打包后的路径）"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


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


def process_invoices(base_path, buyer_keyword, output_path, log_queue):
    """处理发票并生成Excel - 使用队列传递日志"""
    import importlib.util

    def log_callback(msg):
        log_queue.put(("log", msg))

    try:
        extractor_path = get_resource_path("invoice_extractor.py")
        spec = importlib.util.spec_from_file_location("invoice_extractor", extractor_path)
        extractor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(extractor)
        result = extractor.process_invoices(base_path, buyer_keyword, output_path, log_callback)
        log_queue.put(("success", result))
    except Exception as e:
        log_queue.put(("error", str(e)))


class ClickableLabel(tk.Label):
    """可点击的 Label，用作按钮"""

    def __init__(self, parent, text, command=None, bg_color="#007AFF",
                 text_color="white", font_size=12, font_weight="normal", **kwargs):
        if font_weight == "bold":
            font_spec = ("TkDefaultFont", font_size, "bold")
        else:
            font_spec = ("TkDefaultFont", font_size)

        super().__init__(
            parent,
            text=text,
            bg=bg_color,
            fg=text_color,
            font=font_spec,
            cursor="hand2",
            **kwargs
        )

        self.command = command
        self.normal_bg = bg_color
        self.hover_bg = self._darken_color(bg_color)

        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _darken_color(self, hex_color, factor=0.8):
        if not hex_color.startswith('#'):
            return hex_color
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.config(bg=self.hover_bg)

    def _on_leave(self, event):
        self.config(bg=self.normal_bg)


class MainWindow:
    """主窗口"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("发票提取器")
        self.root.geometry("600x500")

        # 日志队列（线程安全）
        self.log_queue = queue.Queue()

        # 检查依赖
        deps_ok, deps_msg = check_and_install_deps()
        self.deps_ok = deps_ok

        self.setup_ui()

        # 启动日志处理
        self.process_log_queue()

        if not deps_ok:
            self.log(f"⚠️ {deps_msg}")
            self.log("请点击下方按钮安装依赖...")

    def setup_ui(self):
        # 主框架
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题栏
        title_frame = tk.Frame(main_frame, bg="white")
        title_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            title_frame,
            text="📄 发票提取",
            font=("TkDefaultFont", 14, "bold"),
            bg="white",
            fg="#1d1d1f"
        ).pack(side=tk.LEFT)

        # 配置区域
        config_frame = tk.LabelFrame(main_frame, text="配置选项", padx=15, pady=15, bg="white")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        # 发票目录
        tk.Label(config_frame, text="发票目录:", bg="white").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.dir_entry = tk.Entry(config_frame, width=40)
        self.dir_entry.grid(row=0, column=1, pady=8, padx=5, sticky=tk.W)

        ClickableLabel(
            config_frame,
            text=" 浏览 ",
            command=self.browse_dir,
            bg_color="#e0e0e0",
            text_color="#333",
            font_size=9
        ).grid(row=0, column=2, padx=5)

        # 购买方关键词
        tk.Label(config_frame, text="购买方关键词:", bg="white").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.buyer_entry = tk.Entry(config_frame, width=40)
        self.buyer_entry.grid(row=1, column=1, pady=8, padx=5, sticky=tk.W)

        # 输出文件
        tk.Label(config_frame, text="输出文件:", bg="white").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.output_entry = tk.Entry(config_frame, width=40)
        self.output_entry.grid(row=2, column=1, pady=8, padx=5, sticky=tk.W)

        ClickableLabel(
            config_frame,
            text=" 浏览 ",
            command=self.browse_output,
            bg_color="#e0e0e0",
            text_color="#333",
            font_size=9
        ).grid(row=2, column=2, padx=5)

        config_frame.columnconfigure(1, weight=1)

        # 日志区域
        log_frame = tk.LabelFrame(main_frame, text="运行日志", padx=10, pady=10, bg="white")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=70, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 按钮区域
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(fill=tk.X)

        # 安装依赖按钮
        self.install_btn = ClickableLabel(
            btn_frame,
            text="  安装依赖  ",
            command=self.install_deps,
            bg_color="#f39c12",
            text_color="white",
            font_size=10
        )
        self.install_btn.pack(side=tk.LEFT, padx=(0, 10))

        if self.deps_ok:
            self.install_btn.config(text="  依赖已安装  ", bg="#cccccc", fg="#666666", cursor="")
            self.install_btn.command = None

        # 开始提取按钮
        self.run_btn = ClickableLabel(
            btn_frame,
            text="  开始提取  ",
            command=self.run_extractor,
            bg_color="#27ae60",
            text_color="white",
            font_size=10,
            font_weight="bold"
        )
        self.run_btn.pack(side=tk.RIGHT)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        tk.Label(main_frame, textvariable=self.status_var,
                relief=tk.SUNKEN, anchor=tk.W, bg="#f5f5f7", fg="#86868b").pack(fill=tk.X, pady=(10, 0))

    def process_log_queue(self):
        """处理日志队列（在主线程中安全地更新UI）"""
        try:
            while True:
                msg_type, msg_data = self.log_queue.get_nowait()
                if msg_type == "log":
                    self._log_safe(msg_data)
                elif msg_type == "success":
                    self._complete_safe(True, msg_data)
                elif msg_type == "error":
                    self._complete_safe(False, msg_data)
        except queue.Empty:
            pass
        # 继续检查队列
        self.root.after(100, self.process_log_queue)

    def _log_safe(self, message):
        """安全的日志方法（主线程调用）"""
        print(message)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def log(self, message):
        """添加日志到队列"""
        print(message)
        self.log_queue.put(("log", message))

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

    def install_deps(self):
        if self.deps_ok:
            return

        self.log("正在安装依赖...")
        self.install_btn.config(text="  安装中...  ")

        def update_callback(success, msg):
            self.log_queue.put(("install_complete", (success, msg)))

        thread = threading.Thread(target=lambda: install_deps(update_callback))
        thread.start()

    def run_extractor(self):
        dir_path = self.dir_entry.get().strip()
        buyer_keyword = self.buyer_entry.get().strip()
        output_path = self.output_entry.get().strip()

        # 清理路径
        dir_path = os.path.expanduser(dir_path)
        if os.name != 'nt':
            dir_path = dir_path.replace('\\ ', ' ')
        if output_path:
            output_path = os.path.expanduser(output_path)
            if os.name != 'nt':
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

        self.run_btn.config(text="  处理中...  ")

        # 在新线程中运行
        thread = threading.Thread(
            target=process_invoices,
            args=(dir_path, buyer_keyword, output_path, self.log_queue)
        )
        thread.daemon = True
        thread.start()

    def _complete_safe(self, success, result):
        """安全的完成方法（主线程调用）"""
        self.run_btn.config(text="  开始提取  ")

        if success:
            self.log("="*50)
            self.log("✅ 处理完成！")
            self.log(f"📁 输出文件: {result}")
            self.log("="*50)
            self.status_var.set("处理完成")
            messagebox.showinfo("完成", f"发票提取完成！\n\n输出文件: {result}")
        else:
            self.log(f"❌ 处理失败: {result}")
            self.status_var.set("处理失败")
            messagebox.showerror("错误", f"处理失败:\n{result}")


def main():
    root = tk.Tk()
    app = MainWindow()
    root.mainloop()


if __name__ == "__main__":
    main()
