# HarmonyDevTools - Python版本

![](https://img.shields.io/badge/状态-稳定-red.svg)
![](https://img.shields.io/badge/启动时间-2024/06/20-green.svg)
![](https://img.shields.io/badge/优先级-NORMAL-blue.svg)
![](https://img.shields.io/badge/语言-Python-blue.svg)

本项目为HarmonyOS/OpenHarmony的 toolchains 工具提供Python Tkinter UI操作界面，方便使用。

## 1. 版本说明

这是原C# WPF项目的Python Tkinter版本，保持了相同的功能特性：

hdc功能支持:
- 枚举设备/连接设备
- 重启hdc
- 版本信息显示
- 安装、卸载应用
- 导出照片
- 获取手机的UDID
- 其他命令的执行（手动输入执行）

## 2. 环境要求

- Python 3.7+
- Windows操作系统
- HarmonyOS/OpenHarmony SDK（包含toolchains目录）

## 3. 安装和运行

### 3.1 直接运行

1. 确保已安装Python 3.7或更高版本
2. 下载项目文件
3. 确保`toolchains`目录包含`hdc.exe`文件
4. 运行主程序：

**方式一：使用启动脚本（推荐）**
```bash
run.bat
```

**方式二：直接运行Python文件**
```bash
python main.py
```

### 3.2 安装依赖（可选）

如果需要额外的功能，可以安装可选依赖：

```bash
pip install -r requirements.txt
```

## 4. 打包为exe文件

### 4.1 使用项目自带的构建脚本（推荐）

```bash
# 运行构建脚本
python build.py
```

构建脚本会：
- 自动检查PyInstaller是否安装
- 自动清理之前的构建文件
- 构建HarmonyDevTools_v版本号.exe（包含版本信息）
- 自动创建完整的发布包
- 生成说明文档
- 构建完成后自动清理临时文件

### 4.2 使用PyInstaller手动打包

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包为exe文件
pyinstaller --onefile --windowed --name HarmonyDevTools_v版本号 main.py
```

### 4.3 版本管理

```bash
# 更新版本号
python update_version.py

# 查看当前版本
# 运行 update_version.py 会显示当前版本
```

**版本号格式**: x.y.z (例如: 1.4.0)
- 文件名格式: HarmonyDevTools_v1_4_0.exe
- 程序内显示: 1.4.0（构建时通过命令行参数传递）
- 版本号来源: version_info.txt（main.py中的VERSION变量用于开发调试）

### 4.4 使用auto-py-to-exe（GUI工具）

```bash
# 安装auto-py-to-exe
pip install auto-py-to-exe

# 启动GUI打包工具
auto-py-to-exe
```

## 5. 项目结构

```
HarmonyDevTools_Python/
├── main.py              # 主程序文件
├── build.py             # 构建脚本
├── version_info.txt     # 版本信息文件
├── update_version.py    # 版本更新脚本
├── requirements.txt     # Python依赖文件
├── README_Python.md     # 说明文档
├── toolchains/          # 工具链目录
│   ├── hdc.exe         # HDC工具
│   └── libusb_shared.dll
└── build/              # 打包输出目录（可选）
```

## 6. 功能说明

### 6.1 设备管理
- **列举设备**: 显示所有可用的HarmonyOS设备
- **连接设备**: 通过connect key连接指定设备
- **重启hdc**: 重启HDC服务

### 6.2 应用管理
- **安装hap**: 安装HarmonyOS应用包
  - 替换安装: 覆盖已存在的应用
  - 允许降级: 允许安装较低版本
  - 动态授权: 动态授权安装
- **卸载应用**: 根据包名卸载应用

### 6.3 文件操作
- **导出照片**: 从设备导出照片到本地
- **自定义命令**: 执行任意hdc命令

### 6.4 系统信息
- **版本信息**: 显示HDC版本信息
- **UDID**: 获取设备唯一标识符

## 7. 与原C#版本的对比

| 特性 | C# WPF版本 | Python Tkinter版本 |
|------|------------|-------------------|
| 运行环境 | .NET Core 6.0 | Python 3.7+ |
| UI框架 | WPF | Tkinter |
| 打包大小 | 较大 | 较小 |
| 跨平台 | Windows | Windows/Linux/macOS |
| 开发难度 | 中等 | 简单 |
| 维护成本 | 中等 | 低 |

## 8. 故障排除

### 8.1 常见问题

1. **找不到hdc.exe**
   - 确保`toolchains`目录存在且包含`hdc.exe`
   - 检查文件路径是否正确

2. **Python未安装**
   - 从[Python官网](https://www.python.org/downloads/)下载并安装Python

3. **tkinter模块错误**
   - 大多数Python安装都包含tkinter
   - 如果缺失，请重新安装Python并确保选中tkinter选项

### 8.2 日志查看

程序运行时会输出日志信息，可以通过查看控制台输出来诊断问题。

## 9. 开发说明

### 9.1 代码结构

- `HdcUtil`: HDC工具类，负责执行命令
- `HarmonyDevTools`: 主界面类，负责UI交互
- `main()`: 程序入口函数

### 9.2 扩展功能

如需添加新功能，可以：

1. 在`HdcUtil`类中添加新的静态方法
2. 在`HarmonyDevTools`类中添加对应的UI元素和事件处理
3. 更新UI布局

## 10. 许可证

本项目遵循原项目的许可证条款。

## 11. 贡献

欢迎提交Issue和Pull Request来改进这个项目。

---

**注意**: 使用前请确保已正确安装HarmonyOS/OpenHarmony SDK，并且`toolchains`目录包含所需的工具文件。
