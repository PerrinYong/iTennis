@echo off
REM What2Eat 开发环境快速启动脚本
REM 
REM 使用说明:
REM   dev.bat           - 显示开发菜单
REM   dev.bat test      - 运行测试
REM   dev.bat run       - 启动程序
REM   dev.bat install   - 安装依赖

echo.
echo ========================================
echo    What2Eat 开发环境 - 快速工具
echo ========================================

cd /d "%~dp0"

REM 设置虚拟环境Python路径
set PYTHON_EXE=..\..\..venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

set ACTION=%1
if "%ACTION%"=="" goto show_menu

if "%ACTION%"=="test" goto run_tests
if "%ACTION%"=="run" goto run_app
if "%ACTION%"=="install" goto install_deps
if "%ACTION%"=="clean" goto clean_cache

echo ❌ 未知操作: %ACTION%
goto show_menu

:show_menu
echo.
echo 🛠️  可用操作:
echo.
echo   test     - 运行单元测试
echo   run      - 启动主程序
echo   install  - 安装开发依赖
echo   clean    - 清理缓存文件
echo.
echo 💡 使用方式: dev.bat [操作]
echo    例如: dev.bat test
echo.
pause
goto end

:run_tests
echo 🧪 运行测试...
call run_tests.bat unit
goto end

:run_app
echo 🚀 启动程序...
call run_app.bat
goto end

:install_deps
echo 📦 安装开发依赖...
"%PYTHON_EXE%" -m pip install pytest pytest-mock pytest-cov coverage pyyaml black flake8
echo ✅ 依赖安装完成
pause
goto end

:clean_cache
echo 🧹 清理缓存文件...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "src\__pycache__" rmdir /s /q "src\__pycache__"
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
if exist "tests\__pycache__" rmdir /s /q "tests\__pycache__"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
if exist "htmlcov" rmdir /s /q "htmlcov"
if exist ".coverage" del ".coverage"
if exist "*.pyc" del /s "*.pyc"
echo ✅ 缓存文件清理完成
pause
goto end

:end