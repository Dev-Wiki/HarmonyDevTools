#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HarmonyDevTools
提供更丰富的功能和更好的用户体验
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Menu
import subprocess
import os
import threading
import datetime
import logging
import json
import ctypes
import webbrowser
import re
from pathlib import Path
from typing import Optional, Dict, Any

# 版本信息
VERSION = "1.4.0"

# --- UI 界面 ---
# 启用 DPI 感知（避免高分屏模糊）
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('harmony_dev_tools.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def center_window(win, width, height):
    """让窗口在屏幕中央显示"""
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

def get_version():
    """获取版本号"""
    import sys
    # 检查是否有命令行参数传入版本号
    if len(sys.argv) > 1 and sys.argv[1].startswith('--version='):
        return sys.argv[1].split('=', 1)[1]
    return VERSION

class Config:
    """配置管理类"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "window_size": "970x600",
            "theme": "default",
            "auto_connect": False,
            "default_target": "",
            "recent_commands": [],
            "max_recent_commands": 10,
            "log_level": "INFO"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
        
        return default_config
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """设置配置值"""
        self.config[key] = value
        self.save_config()

class HdcUtil:
    """HDC工具类，用于执行hdc命令"""
    
    def __init__(self):
        self.hdc_path = "toolchains/hdc.exe"
        self.check_hdc_path()
    
    def check_hdc_path(self):
        """检查hdc.exe路径"""
        if not os.path.exists(self.hdc_path):
            logger.warning(f"HDC路径不存在: {self.hdc_path}")
            # 尝试查找hdc.exe
            possible_paths = [
                "hdc.exe",
                "toolchains/hdc.exe",
                "toolchains\\hdc.exe",
                "../toolchains/hdc.exe"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    self.hdc_path = path
                    logger.info(f"找到HDC路径: {self.hdc_path}")
                    break
    
    @staticmethod
    def run_cmd(parameter="", with_exit=True):
        """使用cmd.exe执行命令"""
        output = []
        try:
            if parameter:
                cmd = ["cmd.exe", "/c", parameter]
                if with_exit:
                    cmd.append("&exit")
            else:
                cmd = ["cmd.exe"]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            stdout, stderr = process.communicate()
            
            # 过滤输出
            for line in stdout.split('\n'):
                if line and not line.startswith("(c) Microsoft") and not line.startswith("Microsoft Windows"):
                    output.append(line)
            
            if stderr:
                output.append(f"ERROR: {stderr}")
                
        except Exception as e:
            logger.error(f"执行命令失败: {e}")
            output.append(f"ERROR: {e}")
            
        return '\n'.join(output)
    
    def run_exe(self, exe_path, arguments=""):
        """使用指定的exe文件执行命令"""
        output = []
        try:
            process = subprocess.Popen(
                [exe_path] + arguments.split() if arguments else [exe_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                output.extend(stdout.split('\n'))
            
            if stderr:
                output.append(f"ERROR: {stderr}")
                
        except Exception as e:
            logger.error(f"执行exe失败: {e}")
            output.append(f"ERROR: {e}")
            
        return '\n'.join(output)
    
    def export_file(self, origin_path):
        """导出文件"""
        formatted_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        HdcUtil.run_cmd(f"mkdir {formatted_date}")
        command = f"file recv {origin_path} ./{formatted_date}"
        return self.run_exe(self.hdc_path, command)
    
    def run_command(self, command):
        """运行hdc命令"""
        return self.run_exe(self.hdc_path, command)

class CommandHistory:
    """命令历史管理"""
    
    def __init__(self, max_history=50):
        self.max_history = max_history
        self.history = []
        self.current_index = -1
    
    def add_command(self, command):
        """添加命令到历史"""
        if command and command not in self.history:
            self.history.append(command)
            if len(self.history) > self.max_history:
                self.history.pop(0)
        self.current_index = len(self.history)
    
    def get_previous(self):
        """获取上一条命令"""
        if self.history and self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]
        return ""
    
    def get_next(self):
        """获取下一条命令"""
        if self.history and self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        return ""
    
    def get_recent(self, count=10):
        """获取最近的命令"""
        return self.history[-count:] if self.history else []

class HarmonyDevTools:
    """Harmony开发工具主界面"""
    
    def __init__(self, root):
        self.root = root
        self.config = Config()
        self.hdc_util = HdcUtil()
        self.command_history = CommandHistory()
        
        # 设置窗口
        self.setup_window()
        self.setup_menu()
        self.setup_ui()
        self.setup_bindings()
        
        # 加载配置
        self.load_config()
        
    def setup_window(self):
        """设置窗口"""
        self.root.title("HDC Tools")
        self.root.minsize(970, 600)    # 最小大小限制
        self.root.resizable(False, True)  # 允许水平 & 垂直拉伸
        center_window(self.root, 970, 600)  # 初始化居中
        
        # 设置图标（如果存在）
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存日志", command=self.save_log)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 工具菜单
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="清理HDC进程", command=self.kill_hdc_processes)
        tools_menu.add_command(label="检查HDC状态", command=self.check_hdc_status)
        tools_menu.add_separator()
        tools_menu.add_command(label="打开日志文件", command=self.open_log_file)
        
        # 帮助菜单
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="查看帮助", command=self.show_help)
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        
        # 第一行：设备操作
        row = 0
        ttk.Button(main_frame, text="列举设备", width=12, command=self.list_devices).grid(
            row=row, column=0, padx=(0, 5), pady=5)
        
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(main_frame, textvariable=self.target_var, width=30)
        target_entry.grid(row=row, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(main_frame, text="连接设备", width=12, command=self.connect_device).grid(
            row=row, column=3, padx=5, pady=5)
        
        ttk.Button(main_frame, text="重启hdc", width=12, command=self.restart_hdc).grid(
            row=row, column=4, padx=5, pady=5)
        
        ttk.Button(main_frame, text="版本信息", width=12, command=self.check_version).grid(
            row=row, column=5, padx=(5, 0), pady=5)
        
        # 第二行：安装操作
        row += 1
        install_frame = ttk.LabelFrame(main_frame, text="安装操作", padding="5")
        install_frame.grid(row=row, column=0, columnspan=3, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(install_frame, text="安装hap", width=12, command=self.install_hap).pack(side=tk.LEFT)
        
        self.replace_var = tk.BooleanVar()
        ttk.Checkbutton(install_frame, text="替换安装", variable=self.replace_var).pack(side=tk.LEFT, padx=(10, 0))
        
        self.downgrade_var = tk.BooleanVar()
        ttk.Checkbutton(install_frame, text="允许降级", variable=self.downgrade_var).pack(side=tk.LEFT, padx=(10, 0))
        
        self.dynamic_var = tk.BooleanVar()
        ttk.Checkbutton(install_frame, text="动态授权", variable=self.dynamic_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # 卸载操作
        uninstall_frame = ttk.LabelFrame(main_frame, text="卸载操作", padding="5")
        uninstall_frame.grid(row=row, column=3, columnspan=3, padx=(5, 0), pady=5, sticky=(tk.W, tk.E))
        
        self.package_name_var = tk.StringVar()
        ttk.Entry(uninstall_frame, textvariable=self.package_name_var, width=25).pack(side=tk.LEFT)
        
        ttk.Button(uninstall_frame, text="卸载应用", width=12, command=self.uninstall_app).pack(side=tk.LEFT, padx=(10, 0))
        
        # 第三行：其他操作
        row += 1
        ttk.Button(main_frame, text="导出照片", width=12, command=self.export_photo).grid(
            row=row, column=0, padx=(0, 5), pady=5)
        
        ttk.Button(main_frame, text="UDID", width=12, command=self.get_udid).grid(
            row=row, column=1, padx=5, pady=5)
        
        # 第四行：命令执行
        row += 1
        self.command_var = tk.StringVar()
        command_entry = ttk.Entry(main_frame, textvariable=self.command_var, width=50)
        command_entry.grid(row=row, column=0, columnspan=5, padx=(0, 5), pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(main_frame, text="执行", width=12, command=self.execute_command).grid(
            row=row, column=5, padx=(5, 0), pady=5)
        
        # 第五行：结果显示
        row += 1
        result_frame = ttk.LabelFrame(main_frame, text="执行结果", padding="5")
        result_frame.grid(row=row, column=0, columnspan=6, padx=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建结果显示区域
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, width=80)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置结果区域网格权重
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        # 保存控件引用
        self.target_entry = target_entry
        self.command_entry = command_entry
    
    def setup_bindings(self):
        """设置事件绑定"""
        # 命令输入框绑定回车键
        self.command_entry.bind('<Return>', lambda e: self.execute_command())
        
        # 命令输入框绑定上下箭头键（历史记录）
        self.command_entry.bind('<Up>', lambda e: self.show_command_history('up'))
        self.command_entry.bind('<Down>', lambda e: self.show_command_history('down'))
        
        # 窗口大小改变事件
        self.root.bind('<Configure>', self.on_window_resize)
    
    def show_command_history(self, direction):
        """显示命令历史"""
        if direction == 'up':
            command = self.command_history.get_previous()
        else:
            command = self.command_history.get_next()
        
        if command:
            self.command_var.set(command)
            # 选中所有文本
            self.command_entry.select_range(0, tk.END)
    
    def on_window_resize(self, event):
        """窗口大小改变事件"""
        if event.widget == self.root:
            # 保存窗口大小到配置
            self.config.set("window_size", f"{event.width}x{event.height}")
    
    def load_config(self):
        """加载配置"""
        # 加载默认目标
        default_target = self.config.get("default_target", "")
        if default_target:
            self.target_var.set(default_target)
    
    def append_result(self, text):
        """添加结果到显示区域"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.result_text.insert(tk.END, f"[{timestamp}] {text}\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()
    
    def execute_command_async(self, command):
        """异步执行命令"""
        def run():
            self.append_result(f"执行命令: {command}")
            result = self.hdc_util.run_command(command)
            self.append_result(f"执行结果: {result}")
            
            # 添加到命令历史
            self.command_history.add_command(command)
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
    
    def list_devices(self):
        """列举设备"""
        self.command_var.set("list targets -v")
        self.execute_command_async("list targets -v")
    
    def connect_device(self):
        """连接设备"""
        target = self.target_var.get().strip()
        if not target:
            messagebox.showwarning("警告", "请输入connect key")
            return
        command = f"-t {target}"
        self.command_var.set(command)
        self.execute_command_async(command)
        
        # 保存到配置
        self.config.set("default_target", target)
    
    def restart_hdc(self):
        """重启hdc"""
        self.command_var.set("kill -r")
        self.execute_command_async("kill -r")
    
    def check_version(self):
        """检查版本信息"""
        self.command_var.set("checkserver")
        self.execute_command_async("checkserver")
    
    def install_hap(self):
        """安装hap文件"""
        file_path = filedialog.askopenfilename(
            title="选择hap文件",
            filetypes=[("HarmonyNEXT", "*.hap"), ("所有文件", "*.*")]
        )
        
        if file_path:
            # 统一路径格式，确保使用正确的路径分隔符
            normalized_path = os.path.normpath(file_path)
            self.append_result(f"选择文件: {normalized_path}")
            
            command = "install"
            if self.replace_var.get():
                command += " -r"
            if self.downgrade_var.get():
                command += " -d"
            if self.dynamic_var.get():
                command += " -g"
            
            command += f" \"{normalized_path}\""
            self.command_var.set(command)
            self.execute_command_async(command)
    
    def uninstall_app(self):
        """卸载应用"""
        package_name = self.package_name_var.get().strip()
        if not package_name:
            messagebox.showwarning("警告", "请输入包名")
            return
        command = f"uninstall {package_name}"
        self.command_var.set(command)
        self.execute_command_async(command)
    
    def export_photo(self):
        """导出照片"""
        self.export_file("/storage/media/100/local/files/Photo")
    
    def export_file(self, path):
        """导出文件"""
        def run():
            formatted_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            HdcUtil.run_cmd(f"mkdir {formatted_date}")
            self.append_result(f"创建目录: {formatted_date}")
            self.append_result(f"导出 {path} 到 {formatted_date}")
            result = self.hdc_util.export_file(path)
            self.append_result(f"导出结果: {result}")
            
            # 导出完成后打开文件夹
            try:
                if os.path.exists(formatted_date):
                    os.startfile(formatted_date)
                    self.append_result(f"已打开导出目录: {formatted_date}")
            except Exception as e:
                self.append_result(f"打开文件夹失败: {e}")
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
    
    def get_udid(self):
        """获取UDID"""
        self.command_var.set("shell bm get --udid")
        self.execute_command_async("shell bm get --udid")
    
    def execute_command(self):
        """执行命令"""
        command = self.command_var.get().strip()
        if not command:
            messagebox.showwarning("警告", "请输入命令")
            return
        self.execute_command_async(command)
    
    def save_log(self):
        """保存日志"""
        file_path = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.get(1.0, tk.END))
                messagebox.showinfo("成功", f"日志已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
    
    def kill_hdc_processes(self):
        """清理HDC进程"""
        def run():
            result = HdcUtil.run_cmd("taskkill /IM hdc.exe")
            self.append_result(f"清理HDC进程: {result}")
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
    
    def check_hdc_status(self):
        """检查HDC状态"""
        self.execute_command_async("checkserver")
    
    def open_log_file(self):
        """打开日志文件"""
        log_file = "harmony_dev_tools.log"
        if os.path.exists(log_file):
            try:
                os.startfile(log_file)
            except:
                messagebox.showinfo("信息", f"日志文件位置: {os.path.abspath(log_file)}")
        else:
            messagebox.showinfo("信息", "暂无日志文件")
    
    def show_about(self):
        """显示关于信息"""
        version = get_version()
        about_text = f"""HarmonyDevTools

版本: {version}
作者: DevWiki
功能: HarmonyOS/OpenHarmony开发工具

基于原C# WPF项目转换而来，
使用Python Tkinter重新实现。

支持功能:
- 设备管理
- 应用安装/卸载
- 文件导出
- 命令执行
"""
        messagebox.showinfo("关于", about_text)
    
    def show_help(self):
        """显示帮助"""
        help_text = """使用说明:

1. 设备连接:
   - 点击"列举设备"查看可用设备
   - 输入connect key后点击"连接设备"

2. 应用管理:
   - 选择hap文件进行安装
   - 输入包名进行卸载

3. 文件操作:
   - 点击"导出照片"导出设备照片
   - 点击"导出日志"导出指定应用的日志文件
   - 使用自定义命令执行其他操作

4. 快捷键:
   - 命令输入框支持上下箭头键浏览历史
   - 回车键执行命令

5. 日志管理:
   - 可通过菜单保存执行日志
   - 日志文件自动保存在程序目录
"""
        messagebox.showinfo("帮助", help_text)
    
    def on_closing(self):
        """窗口关闭时的处理"""
        try:
            # 保存配置
            self.config.save_config()
            
            # 清理HDC进程
            result = HdcUtil.run_cmd("taskkill /IM hdc.exe")
            self.append_result(result)
        except:
            pass
        self.root.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = HarmonyDevTools(root)
    
    # 绑定关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 启动应用
    root.mainloop()

if __name__ == "__main__":
    main()
