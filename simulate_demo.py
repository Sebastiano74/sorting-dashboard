"""
simulate_demo.py — Simulazione 10 pezzi per demo/registrazione
==============================================================
Autore: Sebastiano Giaquinta

Simula 10 pezzi smistati con timing realistico per la registrazione
del video LinkedIn. Avvia PRIMA la dashboard su http://localhost:5000
poi esegui questo script.
"""

import requests
import time
from datetime import datetime
import random

URL = "http://127.0.0.1:5000/evento"

# Sequenza di 10 pezzi — mix realistico
PEZZI = [
    {"colore": "BIANCO", "bin": "Bin Bianco", "passi_encoder": 11,  "tempo_elaborazione": 2.1},
    {"colore": "BLU",    "bin": "Bin Blu",    "passi_encoder": 27,  "tempo_elaborazione": 2.4},
    {"colore": "BIANCO", "bin": "Bin Bianco", "passi_encoder": 11,  "tempo_elaborazione": 1.9},
    {"colore": "SCARTO", "bin": "Scarto",     "passi_encoder": 300, "tempo_elaborazione": 3.1},
    {"colore": "BLU",    "bin": "Bin Blu",    "passi_encoder": 27,  "tempo_elaborazione": 2.2},
    {"colore": "BIANCO", "bin": "Bin Bianco", "passi_encoder": 11,  "tempo_elaborazione": 2.0},
    {"colore": "BLU",    "bin": "Bin Blu",    "passi_encoder": 27,  "tempo_elaborazione": 2.3},
    {"colore": "BIANCO", "bin": "Bin Bianco", "passi_encoder": 11,  "tempo_elaborazione": 1.8},
    {"colore": "SCARTO", "bin": "Scarto",     "passi_encoder": 300, "tempo_elaborazione": 2.9},
    {"colore": "BLU",    "bin": "Bin Blu",    "passi_encoder": 27,  "tempo_elaborazione": 2.1},
]

def simula():
    print("=" * 50)
    print("  Sorting Line — Simulazione Demo")
    print("  Assicurati che Flask sia avviato!")
    print("=" * 50)
    print()

    for i, pezzo in enumerate(PEZZI, 1):
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        payload = {
            "colore"            : pezzo["colore"],
            "bin"               : pezzo["bin"],
            "passi_encoder"     : pezzo["passi_encoder"],
            "timestamp_inizio"  : ts,
            "tempo_elaborazione": pezzo["tempo_elaborazione"],
        }

        print(f"[{i:02d}/10] Invio pezzo → {pezzo['colore']:8s} | bin: {pezzo['bin']:12s} | passi: {pezzo['passi_encoder']}")

        try:
            r = requests.post(URL, json=payload, timeout=3)
            if r.status_code == 200:
                print(f"        ✓ Ricevuto dalla dashboard")
            else:
                print(f"        ✗ Errore {r.status_code}")
        except Exception as e:
            print(f"        ✗ Connessione fallita: {e}")

        # Pausa realistica tra un pezzo e l'altro (5-7 secondi)
        # così l'animazione del nastro si vede bene nel video
        pausa = 5 + random.uniform(0, 2)
        print(f"        ⏱ Prossimo pezzo tra {pausa:.1f}s...")
        print()
        time.sleep(pausa)

    print("=" * 50)
    print("  Simulazione completata! 10 pezzi smistati.")
    print("=" * 50)

if __name__ == "__main__":
    simula()
