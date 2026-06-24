@echo off
echo ============================================
echo  Sorting Line Dashboard — Setup Windows
echo  Autore: Sebastiano Giaquinta
echo ============================================
echo.

echo [1/3] Creazione ambiente virtuale...
python -m venv .venv

echo [2/3] Attivazione e installazione dipendenze...
call .venv\Scripts\activate
pip install -r requirements.txt

echo [3/3] Avvio dashboard...
echo.
echo Dashboard disponibile su http://localhost:5000
echo.
python app.py