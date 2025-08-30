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
    echo [错误] 未找到Hugo命令
    pause
    exit /b 1
)

echo [信息] 服务器启动中...
echo [信息] 访问地址: http://localhost:%PORT%
echo.

hugo server %HUGO_ARGS% --port %PORT%

echo.
echo [信息] 服务器已停止
pause