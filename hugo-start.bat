@echo off
setlocal

REM 设置控制台编码为UTF-8，解决VSCode中文乱码问题
chcp 65001 >nul 2>&1

REM 设置默认参数
set PORT=1313
set HUGO_ARGS=--disableFastRender --cleanDestinationDir

REM 如果提供了端口参数，使用用户指定的端口
if not "%1"=="" set PORT=%1

echo ======================================
echo 启动 Hugo 开发服务器
echo ======================================
echo 端口: %PORT%
echo 参数: %HUGO_ARGS%
echo ======================================
echo.

REM 检查Hugo是否安装
hugo version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Hugo命令，请确保已安装Hugo
    echo 访问 https://gohugo.io/getting-started/installing/ 获取安装指南
    pause
    exit /b 1
)

echo [信息] 服务器启动中...
echo [信息] 访问地址: http://localhost:%PORT%
echo.

REM 尝试启动Hugo服务器
hugo server %HUGO_ARGS% --port %PORT%
if %errorlevel% equ 0 (
    echo [信息] 服务器正常启动
) else (
    echo [错误] 服务器启动失败，错误代码: %errorlevel%
    echo 可能的原因:
    echo 1. 端口 %PORT% 已被占用，请尝试使用其他端口
    echo 2. 缺少必要的依赖文件
    echo 3. 配置文件存在错误
    echo.
    echo 解决方法:
    echo 1. 运行 hugo-start.bat 1314 使用其他端口
    echo 2. 检查 hugo.yaml 配置文件
    echo 3. 运行 hugo mod tidy 更新模块依赖
    echo.
)

echo.
echo [信息] 服务器已停止
pause