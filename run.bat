@echo off
chcp 65001 >nul
echo ========================================
echo HarmonyDevTools Python版本启动脚本
echo ========================================


REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.7或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查主程序文件是否存在
if not exist "main.py" (
    echo 错误：找不到main.py文件！
    pause
    exit /b 1
)

REM 检查toolchains目录
if not exist "toolchains" (
    echo 警告：找不到toolchains目录，请确保包含hdc.exe文件
    echo.
)

echo 正在启动HarmonyDevTools...
echo.

python main.py

echo.
echo 程序已退出
pause
