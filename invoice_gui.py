#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票提取器 - Windows/Linux 版本
欢迎界面 + 提取界面
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import os
import sys
import webbrowser
import platform


# 版本号
VERSION = "1.0.1"


def get_default_font():
    """获取系统默认中文字体，带回退机制"""
    system = platform.system()

    if system == "Windows":
        return "Microsoft YaHei UI"
    elif system == "Darwin":  # macOS
        return "PingFang SC"
    else:  # Linux
        return "WenQuanYi Micro Hei"


DEFAULT_FONT = get_default_font()


def get_resource_path(relative_path):
    """获取资源文件的绝对路径（兼容 PyInstaller 打包后的路径）

    PyInstaller 打包后，资源文件会被解压到 sys._MEIPASS 临时目录
    """
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


def process_invoices(base_path, buyer_keyword, output_path, log_callback):
    """处理发票并生成Excel"""
    import importlib.util
    extractor_path = get_resource_path("invoice_extractor.py")
    spec = importlib.util.spec_from_file_location("invoice_extractor", extractor_path)
    extractor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extractor)
    return extractor.process_invoices(base_path, buyer_keyword, output_path, log_callback)


class StyledButton(ttk.Button):
    """自定义样式按钮，支持 Windows"""

    def __init__(self, parent, text, command=None, bg="#007AFF", fg="white",
                 font=(DEFAULT_FONT, 11), width=None, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)

        self.bg_color = bg
        self.fg_color = fg

        # 创建唯一样式名称
        style_name = f"CustomButton.{id(self)}"
        self.style = ttk.Style()
        self.style.configure(style_name,
                           font=font,
                           background=bg,
                           foreground=fg,
                           borderwidth=0,
                           focuscolor='none',
                           relief='flat')

        # 设置按钮样式
        self.configure(style=style_name, width=width)


class LinkLabel(tk.Label):
    """可点击的超链接标签"""
    def __init__(self, parent, text, url, **kwargs):
        default_fg = kwargs.pop('fg', '#007AFF')
        kwargs['fg'] = default_fg
        kwargs['cursor'] = 'hand2'
        super().__init__(parent, text=text, **kwargs)

        self.url = url
        self.default_fg = default_fg
        self.hover_fg = '#0051D5'

        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)

    def _on_enter(self, event):
        self.config(fg=self.hover_fg)

    def _on_leave(self, event):
        self.config(fg=self.default_fg)

    def _on_click(self, event):
        webbrowser.open(self.url)


class WelcomeWindow:
    """欢迎窗口"""
    def __init__(self, root):
        self.root = root
        self.root.title("发票提取器")
        self.root.geometry("480x360")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f5f7")

        # 配置 ttk 样式
        self.setup_ttk_style()

        self.center_window()
        self.setup_ui()

    def setup_ttk_style(self):
        """配置 ttk 样式以支持 Windows"""
        self.style = ttk.Style()
        # 使用默认主题
        current_theme = self.style.theme_use()
        # 配置按钮样式
        self.style.configure("Primary.TButton",
                           font=(DEFAULT_FONT, 13, "bold"),
                           background="#007AFF",
                           foreground="white",
                           borderwidth=0,
                           focuscolor='none',
                           relief='flat')
        self.style.map("Primary.TButton",
                      background=[('active', '#0051D5')])

    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """设置界面"""
        # 主容器
        main_frame = tk.Frame(self.root, bg="#f5f5f7")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # 图标/标题区域
        title_frame = tk.Frame(main_frame, bg="#f5f5f7")
        title_frame.pack(pady=(0, 20))

        # 图标
        tk.Label(
            title_frame,
            text="📄",
            font=(DEFAULT_FONT, 48),
            bg="#f5f5f7",
            fg="#007AFF"
        ).pack()

        # 软件名称
        tk.Label(
            title_frame,
            text="发票提取器",
            font=(DEFAULT_FONT, 24, "bold"),
            bg="#f5f5f7",
            fg="#1d1d1f"
        ).pack(pady=(8, 4))

        # 版本号
        tk.Label(
            title_frame,
            text=f"版本 {VERSION}",
            font=(DEFAULT_FONT, 11),
            bg="#f5f5f7",
            fg="#86868b"
        ).pack()

        # 分隔线
        tk.Frame(main_frame, bg="#e5e5e5", height=1).pack(fill=tk.X, pady=(20, 20))

        # 功能说明
        tk.Label(
            main_frame,
            text="智能识别PDF发票，自动提取发票信息\n支持普通发票和高速费发票，一键生成Excel清单",
            font=(DEFAULT_FONT, 12),
            bg="#f5f5f7",
            fg="#3a3a3c",
            justify=tk.CENTER
        ).pack(pady=(0, 20))

        # 按钮区域
        button_frame = tk.Frame(main_frame, bg="#f5f5f7")
        button_frame.pack(pady=(10, 0))

        # 提取发票按钮 - 使用 Label 模拟按钮确保跨平台兼容
        self.extract_btn = tk.Label(
            button_frame,
            text="  提取发票  ",
            font=(DEFAULT_FONT, 13, "bold"),
            bg="#007AFF",
            fg="white",
            cursor="hand2",
            padx=30,
            pady=10
        )
        self.extract_btn.pack()
        self.extract_btn.bind('<Button-1>', lambda e: self.start_extract())
        self.extract_btn.bind('<Enter>', self._on_btn_enter)
        self.extract_btn.bind('<Leave>', self._on_btn_leave)

        # 开发者信息
        info_frame = tk.Frame(main_frame, bg="#f5f5f7")
        info_frame.pack(side=tk.BOTTOM, pady=(20, 0))

        tk.Label(
            info_frame,
            text="开发者: ",
            font=(DEFAULT_FONT, 10),
            bg="#f5f5f7",
            fg="#86868b"
        ).pack(side=tk.LEFT)

        LinkLabel(
            info_frame,
            text="阿凯(MaydayV)",
            url="https://github.com/MaydayV",
            font=(DEFAULT_FONT, 10),
            bg="#f5f5f7"
        ).pack(side=tk.LEFT)

    def _on_btn_enter(self, event):
        """按钮悬停效果"""
        self.extract_btn.config(bg="#0051D5")

    def _on_btn_leave(self, event):
        """按钮离开效果"""
        self.extract_btn.config(bg="#007AFF")

    def start_extract(self):
        """开始提取流程"""
        self.root.destroy()
        MainWindow()


class MainWindow:
    """主窗口"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("发票提取器")
        self.root.geometry("600x500")
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
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题栏
        title_frame = tk.Frame(main_frame, bg="white")
        title_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            title_frame,
            text="📄 发票提取",
            font=(DEFAULT_FONT, 16, "bold"),
            bg="white",
            fg="#1d1d1f"
        ).pack(side=tk.LEFT)

        # 返回按钮 - 使用 Label 模拟
        back_btn = tk.Label(
            title_frame,
            text=" ← 返回 ",
            font=(DEFAULT_FONT, 9),
            bg="#f5f5f7",
            fg="#86868b",
            cursor="hand2"
        )
        back_btn.pack(side=tk.RIGHT)
        back_btn.bind('<Button-1>', lambda e: self.back_to_welcome())

        # 配置区域
        config_frame = tk.LabelFrame(main_frame, text="配置选项", padx=15, pady=15, bg="white")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        # 发票目录
        tk.Label(config_frame, text="发票目录:", bg="white").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.dir_entry = tk.Entry(config_frame, width=40, font=(DEFAULT_FONT, 10))
        self.dir_entry.grid(row=0, column=1, pady=8, padx=5, sticky=tk.W)

        browse_btn1 = tk.Label(
            config_frame,
            text=" 浏览... ",
            bg="#e0e0e0",
            fg="#333",
            cursor="hand2"
        )
        browse_btn1.grid(row=0, column=2, padx=5)
        browse_btn1.bind('<Button-1>', lambda e: self.browse_dir())

        # 购买方关键词
        tk.Label(config_frame, text="购买方关键词:", bg="white").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.buyer_entry = tk.Entry(config_frame, width=40, font=(DEFAULT_FONT, 10))
        self.buyer_entry.grid(row=1, column=1, pady=8, padx=5, sticky=tk.W)

        # 输出文件
        tk.Label(config_frame, text="输出文件:", bg="white").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.output_entry = tk.Entry(config_frame, width=40, font=(DEFAULT_FONT, 10))
        self.output_entry.grid(row=2, column=1, pady=8, padx=5, sticky=tk.W)

        browse_btn2 = tk.Label(
            config_frame,
            text=" 浏览... ",
            bg="#e0e0e0",
            fg="#333",
            cursor="hand2"
        )
        browse_btn2.grid(row=2, column=2, padx=5)
        browse_btn2.bind('<Button-1>', lambda e: self.browse_output())

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
        self.install_btn = tk.Label(
            btn_frame,
            text="  安装依赖  ",
            bg="#f39c12",
            fg="white",
            font=(DEFAULT_FONT, 10),
            cursor="hand2"
        )
        self.install_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.install_btn.bind('<Button-1>', lambda e: self.install_deps())

        if self.deps_ok:
            self.install_btn.config(text="  依赖已安装  ", bg="#cccccc", fg="#666666", cursor="")

        # 开始提取按钮
        self.run_btn = tk.Label(
            btn_frame,
            text="  开始提取  ",
            bg="#27ae60",
            fg="white",
            font=(DEFAULT_FONT, 10, "bold"),
            cursor="hand2"
        )
        self.run_btn.pack(side=tk.RIGHT)
        self.run_btn.bind('<Button-1>', lambda e: self.run_extractor())

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        tk.Label(main_frame, textvariable=self.status_var,
                relief=tk.SUNKEN, anchor=tk.W, bg="#f5f5f7", fg="#86868b").pack(fill=tk.X, pady=(10, 0))

    def back_to_welcome(self):
        """返回欢迎界面"""
        self.root.destroy()
        WelcomeWindow(tk.Tk())

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
        print(message)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def install_deps(self):
        if self.deps_ok:
            return

        def update_callback(success, msg):
            self.install_btn.config(text="  依赖已安装  ", bg="#cccccc", fg="#666666", cursor="")
            self.deps_ok = True
            self.log(msg)

        self.log("正在安装依赖...")
        self.install_btn.config(text="  安装中...  ")
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
    app = WelcomeWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
