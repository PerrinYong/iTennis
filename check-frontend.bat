@echo off
REM 前端开发检查脚本

echo ========================================
echo   AiTeni 前端开发环境检查
echo ========================================
echo.

cd /d "%~dp0aiteni-app"

echo [检查 1] API 配置文件
echo ----------------------------------------
findstr "BASE_URL" miniprogram\utils\api.js
echo.

echo [检查 2] 问卷页文件
echo ----------------------------------------
if exist "miniprogram\pages\questionnaire\questionnaire.js" (
    echo [✓] questionnaire.js 存在
) else (
    echo [✗] questionnaire.js 不存在
)

if exist "miniprogram\pages\questionnaire\questionnaire.js.bak" (
    echo [✓] questionnaire.js.bak 备份存在
) else (
    echo [提示] 无备份文件
)
echo.

echo [检查 3] 后端服务连接测试
echo ----------------------------------------
echo 测试地址: http://localhost:8000/api/health
echo.
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo [✗] 后端服务未响应
    echo [提示] 请先运行 start-backend.bat 启动后端服务
) else (
    echo [✓] 后端服务正常运行
)
echo.

echo [检查 4] 题目配置接口
echo ----------------------------------------
echo 测试地址: http://localhost:8000/api/evaluation/questions
echo.
curl -s http://localhost:8000/api/evaluation/questions | findstr "questions" >nul 2>&1
if errorlevel 1 (
    echo [✗] 题目配置接口异常
    echo [提示] 请检查后端配置文件 aiteni-backend/config/questions.json
) else (
    echo [✓] 题目配置接口正常
)
echo.

echo ========================================
echo   检查完成
echo ========================================
echo.
echo 接下来请：
echo 1. 打开微信开发者工具
echo 2. 导入项目: %~dp0aiteni-app
echo 3. 进入"详情" - "本地设置"
echo 4. 勾选"不校验合法域名..."
echo 5. 点击"编译"运行小程序
echo.

pause
