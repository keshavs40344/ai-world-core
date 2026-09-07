@echo off
title VASTUDA Sovereign Core - Live World Cockpit
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

echo.
echo  =======================================================
echo   VASTUDA Sovereign Core — Autonomous Agent & World
echo   100%% Free Tier · Self-Evolving AI Civilization
echo  =======================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Using system python...
    python run_world.py
) else (
    .venv\Scripts\python.exe run_world.py
)

pause
