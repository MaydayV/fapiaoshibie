#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票提取器 - Windows/Linux 版本
欢迎界面 + 提取界面
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import os
import sys
import webbrowser

# 版本号
VERSION = "1.0.1"


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


class ClickableLabel(tk.Label):
    """可点击的 Label，用作按钮"""

    def __init__(self, parent, text, command=None, bg_color="#007AFF",
                 text_color="white", font_size=12, font_weight="normal", **kwargs):
        # 使用默认字体，只在需要时添加样式
        if font_weight == "bold":
            font_spec = ("TkDefaultFont", font_size, "bold")
        else:
            font_spec = ("TkDefaultFont", font_size)

        # 调用父类初始化 - 移除 Label 不支持的 relief 和 bd
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

        # 绑定事件
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _darken_color(self, hex_color, factor=0.8):
        """使颜色变暗用于悬停效果"""
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
        """处理点击事件"""
        if self.command:
            self.command()

    def _on_enter(self, event):
        """鼠标悬停效果"""
        self.config(bg=self.hover_bg)

    def _on_leave(self, event):
        """鼠标离开效果"""
        self.config(bg=self.normal_bg)


class LinkLabel(tk.Label):
    """可点击的超链接标签"""
    def __init__(self, parent, text, url, **kwargs):
        kwargs['fg'] = kwargs.pop('fg', '#007AFF')
        kwargs['cursor'] = 'hand2'
        super().__init__(parent, text=text, **kwargs)

        self.url = url
        self.default_fg = '#007AFF'
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
        self.root.geometry("480x380")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f5f7")

        self.center_window()
        self.setup_ui()

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
            font=("TkDefaultFont", 44),
            bg="#f5f5f7",
            fg="#007AFF"
        ).pack()

        # 软件名称
        tk.Label(
            title_frame,
            text="发票提取器",
            font=("TkDefaultFont", 20, "bold"),
            bg="#f5f5f7",
            fg="#1d1d1f"
        ).pack(pady=(8, 4))

        # 版本号
        tk.Label(
            title_frame,
            text=f"版本 {VERSION}",
            font=("TkDefaultFont", 10),
            bg="#f5f5f7",
            fg="#86868b"
        ).pack()

        # 分隔线
        tk.Frame(main_frame, bg="#e5e5e5", height=1).pack(fill=tk.X, pady=(15, 15))

        # 功能说明
        tk.Label(
            main_frame,
            text="智能识别PDF发票，自动提取发票信息\n支持普通发票和高速费发票，一键生成Excel清单",
            font=("TkDefaultFont", 11),
            bg="#f5f5f7",
            fg="#3a3a3c",
            justify=tk.CENTER
        ).pack(pady=(0, 20))

        # 按钮区域 - 使用 Frame 确保布局正确
        button_frame = tk.Frame(main_frame, bg="#f5f5f7", height=50)
        button_frame.pack(pady=(10, 0))
        button_frame.pack_propagate(False)  # 防止子组件改变 Frame 大小

        # 提取发票按钮 - 使用自定义 ClickableLabel
        self.extract_btn = ClickableLabel(
            button_frame,
            text="  提取发票  ",
            command=self.start_extract,
            bg_color="#007AFF",
            text_color="white",
            font_size=13,
            font_weight="bold"
        )
        self.extract_btn.pack()

        # 开发者信息
        info_frame = tk.Frame(main_frame, bg="#f5f5f7")
        info_frame.pack(side=tk.BOTTOM, pady=(15, 0))

        tk.Label(
            info_frame,
            text="开发者: ",
            font=("TkDefaultFont", 9),
            bg="#f5f5f7",
            fg="#86868b"
        ).pack(side=tk.LEFT)

        LinkLabel(
            info_frame,
            text="阿凯(MaydayV)",
            url="https://github.com/MaydayV",
            font=("TkDefaultFont", 9),
            bg="#f5f5f7"
        ).pack(side=tk.LEFT)

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
            font=("TkDefaultFont", 14, "bold"),
            bg="white",
            fg="#1d1d1f"
        ).pack(side=tk.LEFT)

        # 返回按钮
        back_btn = ClickableLabel(
            title_frame,
            text=" ← 返回 ",
            command=self.back_to_welcome,
            bg_color="#f5f5f7",
            text_color="#86868b",
            font_size=9
        )
        back_btn.pack(side=tk.RIGHT)

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
            # 禁用点击
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
            self.install_btn.command = None
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
