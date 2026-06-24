@echo off
echo ============================================
echo  Sorting Line Dashboard — Setup Windows
echo  Autore: Sebastiano Giaquinta
echo ============================================
echo.

echo [0/3] Verifica Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] Python non trovato!
    echo.
    echo Vuoi scaricarlo ora? Apro il browser...
    pause
    start https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: durante l'installazione spunta
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Controlla versione minima 3.10
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

echo [INFO] Versione Python rilevata: %PYVER%

if %MAJOR% LSS 3 (
    echo [ERRORE] Python %PYVER% troppo vecchio! Serve almeno Python 3.10
    echo Vuoi aggiornarlo? Apro il browser...
    pause
    start https://www.python.org/downloads/
    exit /b 1
)
if %MAJOR% EQU 3 if %MINOR% LSS 10 (
    echo [ATTENZIONE] Python %PYVER% potrebbe dare problemi.
    echo Consigliamo Python 3.10 o superiore.
    echo.
    echo Vuoi aggiornare? [S/N]
    set /p RISPOSTA=
    if /i "%RISPOSTA%"=="S" (
        start https://www.python.org/downloads/
        echo Riavvia setup dopo l'aggiornamento.
        pause
        exit /b 0
    )
)

echo [OK] Python %PYVER% compatibile!
echo.

echo [1/3] Creazione ambiente virtuale...