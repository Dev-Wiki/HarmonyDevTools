#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HarmonyDevTools Python版本打包脚本
用于将Python项目打包为exe文件
"""

import os
import sys
import subprocess
import shutil
import re
import zipfile
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功！")
        return True
    except subprocess.CalledProcessError:
        print("PyInstaller安装失败！")
        return False

def get_version_from_version_info():
    """从version_info.txt文件中获取版本号"""
    if not os.path.exists("version_info.txt"):
        return "1.0.0"
    
    try:
        with open("version_info.txt", 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r"StringStruct\(u'FileVersion', u'([^']+)'\)", content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"读取version_info.txt版本信息失败: {e}")
    
    return "1.0.0"

def build_with_version(main_file, exe_name, version):
    """使用指定版本号构建exe文件"""
    # 构建命令
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包为单个文件
        "--windowed",                   # 无控制台窗口
        f"--name={exe_name}",           # 输出文件名
        "--icon=icon.ico",              # 图标文件（如果存在）
        "--version-file=version_info.txt",  # 版本信息文件
        "--add-data=toolchains;toolchains",  # 包含toolchains目录
        main_file
    ]

    # 如果图标文件不存在，移除图标参数
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    # 如果版本信息文件不存在，移除版本信息参数
    if not os.path.exists("version_info.txt"):
        cmd = [arg for arg in cmd if not arg.startswith("--version-file")]
    
    return cmd

def get_version_for_filename(version):
    """将版本号转换为文件名格式（只取前三位）"""
    parts = version.split('.')
    if len(parts) >= 3:
        return f"{parts[0]}.{parts[1]}.{parts[2]}"
    return version

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    # 检查主程序文件是否存在
    if not os.path.exists("main.py"):
        print("错误：找不到main.py文件！")
        return False
    
    # 从version_info.txt获取版本号
    version = get_version_from_version_info()
    version_for_filename = get_version_for_filename(version)
    main_file = "main.py"
    exe_name = f"HarmonyDevTools_v{version_for_filename}"
    print(f"构建HarmonyDevTools v{version}...")
    
    # 检查toolchains目录是否存在
    if not os.path.exists("toolchains"):
        print("警告：找不到toolchains目录，请确保包含hdc.exe文件")
    
    # 构建命令
    cmd = build_with_version(main_file, exe_name, version_for_filename)
    
    try:
        subprocess.check_call(cmd)
        print("构建成功！")
        return exe_name
    except subprocess.CalledProcessError as e:
        print(f"构建失败：{e}")
        return False

def create_distribution(exe_name="HarmonyDevTools"):
    """创建发布包"""
    print("创建发布包...")
    
    # 直接使用dist目录作为发布目录
    dist_dir = "dist"
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # 复制toolchains目录到dist
    if os.path.exists("toolchains"):
        toolchains_dest = os.path.join(dist_dir, "toolchains")
        if os.path.exists(toolchains_dest):
            shutil.rmtree(toolchains_dest)
        shutil.copytree("toolchains", toolchains_dest)
        print("已复制toolchains目录到dist")
    
    # 创建适合exe发布包的README
    create_release_readme(dist_dir)
    
    print(f"发布包已创建：{dist_dir}")
    print("发布包包含：")
    print(f"- {exe_name}.exe")
    print("- toolchains/目录")
    print("- README.md")
    return True

def create_release_readme(dist_dir):
    """创建发布版README文件"""
    # 获取当前版本号
    version = get_version_from_version_info()
    version_for_filename = get_version_for_filename(version)
    version_underscore = version_for_filename.replace('.', '_')
    
    readme_content = f"""# HarmonyDevTools

HarmonyOS/OpenHarmony开发工具，提供图形化界面操作HDC工具。

## 功能特性

- **设备管理**: 列举设备、连接设备、重启HDC服务
- **应用管理**: 安装/卸载HarmonyOS应用包
- **文件操作**: 导出设备照片、导出应用日志
- **系统信息**: 获取设备UDID、查看版本信息
- **命令执行**: 支持执行任意HDC命令

## 使用方法

1. **启动程序**: 双击 `HarmonyDevTools_v{version_underscore}.exe` 启动程序
2. **连接设备**: 点击"列举设备"查看可用设备，输入connect key后点击"连接设备"
3. **安装应用**: 选择hap文件，设置安装选项后点击"安装hap"
4. **导出文件**: 点击"导出照片"或"导出日志"从设备导出文件

## 系统要求

- Windows 10/11
- 无需安装Python或其他依赖
- 需要HarmonyOS/OpenHarmony设备

## 注意事项

- 首次使用前请确保设备已开启开发者模式
- 确保toolchains目录包含hdc.exe文件
- 导出文件会自动创建时间戳目录并打开文件夹

## 故障排除

1. **无法连接设备**: 检查设备是否开启USB调试，尝试重启HDC服务
2. **安装失败**: 检查hap文件是否有效，确认设备存储空间充足
3. **导出失败**: 确认设备路径正确，检查文件权限

---
基于原C# WPF项目转换的Python Tkinter版本
版本: {version}
"""
    
    readme_path = os.path.join(dist_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("已创建发布版README.md")

def create_zip_package(exe_name, dist_dir):
    """创建zip压缩包"""
    print("创建zip压缩包...")
    
    # 获取版本号用于zip文件名
    version = get_version_from_version_info()
    version_for_filename = get_version_for_filename(version)
    zip_filename = f"HarmonyDevTools_v{version_for_filename}.zip"
    zip_path = os.path.join(dist_dir, zip_filename)
    
    # 创建zip文件
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加exe文件到HarmonyDevTools_v1.4.0目录下
        exe_path = os.path.join(dist_dir, f"{exe_name}.exe")
        if os.path.exists(exe_path):
            zipf.write(exe_path, f"HarmonyDevTools_v{version_for_filename}/{exe_name}.exe")
            print(f"已添加 {exe_name}.exe 到压缩包")
        
        # 添加toolchains目录下的文件到HarmonyDevTools_v1.4.0/toolchains目录
        toolchains_dir = os.path.join(dist_dir, "toolchains")
        if os.path.exists(toolchains_dir):
            for root, dirs, files in os.walk(toolchains_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 计算相对路径，去掉dist前缀
                    rel_path = os.path.relpath(file_path, dist_dir)
                    # 在zip中创建toolchains子目录
                    arcname = f"HarmonyDevTools_v{version_for_filename}/{rel_path}"
                    zipf.write(file_path, arcname)
                    print(f"已添加 {arcname} 到压缩包")
        
        # 添加README.md到HarmonyDevTools_v1.4.0目录下
        readme_path = os.path.join(dist_dir, "README.md")
        if os.path.exists(readme_path):
            zipf.write(readme_path, f"HarmonyDevTools_v{version_for_filename}/README.md")
            print("已添加 README.md 到压缩包")
    
    print(f"zip压缩包创建成功：{zip_path}")
    return zip_filename


def clean_build_files():
    """清理构建文件"""
    print("清理构建文件...")
    
    # 清理所有构建相关的临时文件
    dirs_to_clean = ["build", "__pycache__"]
    files_to_clean = ["HarmonyDevTools.spec", "HarmonyDevTools_Enhanced.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除目录：{dir_name}")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"已删除文件：{file_name}")
    
    print("清理完成")

def clean_after_build(exe_name):
    """构建完成后清理临时文件"""
    print("清理构建临时文件...")
    
    # 清理build目录
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("已删除build目录")
    
    # 清理spec文件
    spec_files = [f"{exe_name}.spec"]
    for spec_file in spec_files:
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print(f"已删除文件：{spec_file}")
    
    print("构建后清理完成")

def main():
    """主函数"""
    print("=" * 50)
    print("HarmonyDevTools Python版本打包工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误：需要Python 3.7或更高版本！")
        return
    
    print(f"Python版本：{sys.version}")
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("PyInstaller未安装")
        choice = input("是否自动安装PyInstaller？(y/n): ").lower()
        if choice == 'y':
            if not install_pyinstaller():
                return
        else:
            print("请手动安装PyInstaller：pip install pyinstaller")
            return
    
    # 自动清理之前的构建文件
    if os.path.exists("build") or os.path.exists("dist"):
        print("清理之前的构建文件...")
        clean_build_files()
    
    # 构建exe文件
    exe_name = build_exe()
    if exe_name:
        # 自动创建发布包
        create_distribution(exe_name)
        
        # 创建zip压缩包
        zip_filename = create_zip_package(exe_name, "dist")
        
        # 构建完成后清理临时文件
        clean_after_build(exe_name)
        
        print("\n构建完成！")
        print(f"exe文件位置：dist/{exe_name}.exe")
        print(f"zip压缩包：{zip_filename}")
        print("发布包位置：dist/目录")
        print("可以直接分发dist目录或zip压缩包作为完整的发布包")
    else:
        print("构建失败！")

if __name__ == "__main__":
    main()
