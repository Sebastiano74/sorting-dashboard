#!/bin/bash
echo "============================================"
echo " Sorting Line Dashboard — Setup Mac/Linux"
echo " Autore: Sebastiano Giaquinta"
echo "============================================"
echo ""

echo "[0/3] Verifica Python..."
if ! command -v python3 &> /dev/null; then
    echo "[ERRORE] Python3 non trovato!"
    echo "Scarica da: https://www.python.org/downloads/"
    echo "Oppure su Mac: brew install python3"
    exit 1
fi

PYVER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo $PYVER | cut -d. -f1)
MINOR=$(echo $PYVER | cut -d. -f2)

echo "[INFO] Versione Python rilevata: $PYVER"

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo "[ERRORE] Python $PYVER troppo vecchio! Serve almeno Python 3.10"
    echo "Scarica da: https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python $PYVER compatibile!"
echo ""

echo "[1/3] Creazione ambiente virtuale..."
python3 -m venv .venv

echo "[2/3] Installazione dipendenze..."
source .venv/bin/activate
pip install -r requirements.txt

echo "[3/3] Avvio dashboard..."
echo ""
echo "Dashboard disponibile su http://localhost:5000"
echo ""
python app.py