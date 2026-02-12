@echo off
chcp 65001 >nul
title YK 自我進化系統 🧬

echo.
echo ======================================
echo    YK 自我進化系統 - 一鍵啟動
echo ======================================
echo.

:: 檢查虛擬環境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo ❌ 錯誤：虛擬環境不存在！
    echo.
    echo 正在創建虛擬環境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 創建虛擬環境失敗！請確保已安裝 Python 3.8+
        pause
        exit /b 1
    )
    echo ✅ 虛擬環境創建成功
    echo.
)

:: 激活虛擬環境
echo 🔧 激活虛擬環境...
call venv\Scripts\activate.bat

:: 檢查是否需要安裝依賴
echo.
echo 🔍 檢查依賴套件...
python -c "import llama_cpp" 2>nul
if errorlevel 1 (
    echo.
    echo 📦 偵測到缺少依賴套件，正在安裝...
    echo.
    pip install llama-cpp-python google-generativeai schedule
    if errorlevel 1 (
        echo ❌ 依賴安裝失敗！
        pause
        exit /b 1
    )
    echo ✅ 依賴安裝完成
)

:: 檢查 .env.local 文件
if not exist ".env.local" (
    echo.
    echo ⚠️  警告：未找到 .env.local 配置文件
    echo.
    echo 正在創建配置模板...
    (
        echo # YK 自我進化系統配置
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # 可選配置
        echo # EVOLUTION_INTERVAL=3600  # 進化間隔（秒）
        echo # MAX_CONTEXT_TOKENS=4096  # 最大上下文長度
    ) > .env.local
    echo ✅ 已創建 .env.local 模板
    echo.
    echo ⚠️  請編輯 .env.local 並填入您的 Gemini API Key
    echo.
    choice /c YN /m "是否現在打開 .env.local 進行編輯？(Y/N)"
    if errorlevel 2 goto skip_edit
    if errorlevel 1 notepad .env.local
    :skip_edit
    echo.
)

:: 檢查 LLM 模型文件
if not exist "LLM\*.gguf" (
    echo.
    echo ⚠️  警告：未在 LLM\ 資料夾中找到 .gguf 模型文件
    echo.
    echo 請確保已將 Qwen3-4B-Instruct-2507-Q8_0.gguf 放入 LLM\ 資料夾
    echo.
    choice /c YN /m "是否已放置模型文件？(Y/N)"
    if errorlevel 2 (
        echo.
        echo ❌ 請先放置模型文件後再啟動系統
        pause
        exit /b 1
    )
)

:: 創建必要的資料夾
echo.
echo 📁 檢查資料夾結構...
if not exist "memory\instant_memory" mkdir memory\instant_memory
if not exist "memory\short_term_memory" mkdir memory\short_term_memory
if not exist "memory\long_term_memory" mkdir memory\long_term_memory
if not exist "Sandbox\test_modules" mkdir Sandbox\test_modules
if not exist "Sandbox\benchmarks" mkdir Sandbox\benchmarks
if not exist "Sandbox\evolution_logs" mkdir Sandbox\evolution_logs
echo ✅ 資料夾結構完整

:: 顯示系統資訊
echo.
echo ======================================
echo    系統資訊
echo ======================================
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python 未安裝或未加入 PATH
    pause
    exit /b 1
)
echo 虛擬環境: %VIRTUAL_ENV%
echo 工作目錄: %CD%
echo.

:: 啟動系統
echo ======================================
echo    🚀 啟動 YK 自我進化系統
echo ======================================
echo.
echo 啟動模式：完全自主進化
echo 進化週期：每小時自動評估和改進
echo.
echo 按 Ctrl+C 可隨時停止系統
echo.
echo ======================================
echo.

:: 進入 core 目錄並執行
cd core
python main.py

:: 錯誤處理
if errorlevel 1 (
    echo.
    echo ======================================
    echo ❌ 系統執行出錯
    echo ======================================
    echo.
    echo 請檢查：
    echo 1. .env.local 中的 GEMINI_API_KEY 是否正確
    echo 2. LLM 資料夾中是否有 .gguf 模型文件
    echo 3. 虛擬環境是否正確安裝所有依賴
    echo.
)

cd ..
pause
