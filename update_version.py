#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本信息更新脚本
用于快速更新版本号
"""

import re
import os

def update_version_info(new_version):
    """更新版本信息文件"""
    version_file = "version_info.txt"
    
    if not os.path.exists(version_file):
        print(f"错误：找不到 {version_file} 文件")
        return False
    
    # 解析版本号
    version_parts = new_version.split('.')
    if len(version_parts) < 3:
        print("错误：版本号格式应为 x.y.z (例如: 1.4.0)")
        return False
    
    try:
        major, minor, patch = map(int, version_parts[:3])
        build = 0  # 第四位默认为0
    except ValueError:
        print("错误：版本号必须为数字")
        return False
    
    # 读取文件内容
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新版本号
    content = re.sub(r'filevers=\(\d+, \d+, \d+, \d+\)', 
                    f'filevers=({major}, {minor}, {patch}, {build})', content)
    content = re.sub(r'prodvers=\(\d+, \d+, \d+, \d+\)', 
                    f'prodvers=({major}, {minor}, {patch}, {build})', content)
    content = re.sub(r"StringStruct\(u'FileVersion', u'[^']+'\)", 
                    f"StringStruct(u'FileVersion', u'{new_version}')", content)
    content = re.sub(r"StringStruct\(u'ProductVersion', u'[^']+'\)", 
                    f"StringStruct(u'ProductVersion', u'{new_version}')", content)
    
    # 写回文件
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"版本信息已更新为: {new_version}")
    print(f"下次构建将生成: HarmonyDevTools_v{new_version.replace('.', '_')}.exe")
    print("注意：构建时会通过命令行参数传递版本号，main.py中的VERSION变量保持不变")
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("HarmonyDevTools 版本更新工具")
    print("=" * 50)
    
    # 显示当前版本
    if os.path.exists("version_info.txt"):
        with open("version_info.txt", 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r"StringStruct\(u'FileVersion', u'([^']+)'\)", content)
            if match:
                current_version = match.group(1)
                print(f"当前版本: {current_version}")
    
    # 获取新版本号
    print("\n请输入新版本号 (格式: x.y.z，例如: 1.4.0)")
    new_version = input("新版本号: ").strip()
    
    if not new_version:
        print("未输入版本号，操作取消")
        return
    
    # 更新版本信息
    if update_version_info(new_version):
        print("\n版本更新完成！")
        print("现在可以运行 python build.py 来构建新版本")
    else:
        print("\n版本更新失败！")

if __name__ == "__main__":
    main()
