@echo off
:: Project Genesis — Dashboard Launcher
title Genesis Dashboard

chcp 65001 >nul
set PYTHONUTF8=1

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

echo Starting Genesis Operator Dashboard...
echo Open your browser at: http://localhost:8501
echo.

.venv\Scripts\python.exe -m streamlit run dashboard\app.py --server.port 8501

pause
