@echo off
title QKD_Mate - Quantum Key Distribution Client

echo.
echo ======================================
echo   QKD_Mate - Quick Start
echo ======================================
echo.

REM Controlla se Python è disponibile
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato nel PATH
    echo Installa Python 3.10+ e riprova
    pause
    exit /b 1
)

REM Avvia quick start
python quick_start.py

pause