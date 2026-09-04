@echo off
:: ============================================================
:: Project Genesis — One-Click Launch Script (Windows)
:: ============================================================
:: Usage: Double-click start_genesis.bat  OR  run from cmd
:: ============================================================

title Project Genesis Engine

echo.
echo  =========================================
echo   Project Genesis - Autonomous Foundry
echo  =========================================
echo.

:: Set UTF-8 for Unicode support
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

:: Check venv exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Run: python -m venv .venv
    echo Then: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

:: Create .env if missing
if not exist ".env" (
    echo [INFO] Creating .env from template...
    copy .env.example .env >nul
    echo [INFO] .env created. Edit it to set your Ollama model.
)

echo [1/3] Checking Ollama...
.venv\Scripts\python.exe -c "import requests; from genesis import config; requests.get(f'{config.OLLAMA_HOST}/api/tags', headers=config.OLLAMA_HEADERS, timeout=5).raise_for_status()" 2>nul
if errorlevel 1 (
    echo [INFO] Ollama endpoint unreachable. Attempting to start local Ollama...
    start /B "" "%LOCALAPPDATA%\Microsoft\WinGet\Links\ollama.exe" serve >nul 2>&1
    timeout /t 3 /nobreak >nul
    .venv\Scripts\python.exe -c "import requests; from genesis import config; requests.get(f'{config.OLLAMA_HOST}/api/tags', headers=config.OLLAMA_HEADERS, timeout=5).raise_for_status()" 2>nul
    if errorlevel 1 (
        echo [WARN] Ollama could not be started automatically.
        echo        Running in DRY-RUN mode instead.
        set DRY_RUN=--dry-run
    ) else (
        echo [OK]   Ollama auto-started successfully.
        set DRY_RUN=
    )
) else (
    echo [OK]   Ollama is running.
    set DRY_RUN=
)

echo [2/3] Starting Genesis Engine...
echo.

.venv\Scripts\python.exe -m genesis.controller %DRY_RUN% %*

pause
