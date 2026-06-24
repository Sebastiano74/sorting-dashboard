# 🏭 Sorting Line Dashboard

**Dashboard web in tempo reale per la linea di smistamento automatico fischertechnik TXT 4.0**

> Sviluppata nell'ambito del corso **GOL25-2-011/073 — Tecnico Specializzato in Logistica, Spedizioni e Trasporti**  
> Istituto Design Palladio — Verona, Giugno 2026

---

## 👤 Autore

**Sebastiano Giaquinta**  
📧 vitosebastiano.giaquinta@gmail.com  
📱 +39 393 855 7555  
🔗 [linkedin.com/in/vito-sebastiano-giaquinta](https://www.linkedin.com/in/vito-sebastiano-giaquinta-74b185202)  
💻 [github.com/Sebastiano74](https://github.com/Sebastiano74)

---

## 📋 Descrizione

La dashboard sostituisce la console di default di ROBO Pro Coding con un'interfaccia web professionale che mostra in tempo reale:

- **Nastro trasportatore animato** con il cilindro che si muove, viene scansionato e smistato
- **KPI industriali** — totale pezzi, accuracy, tempo medio di elaborazione
- **Log eventi** con timestamp europeo, colore rilevato e passi encoder
- **Storico sessioni** con database SQLite persistente
- **Assistente AI** (Groq) che analizza i dati di produzione in italiano
- **Auto-discovery IP** — il TXT 4.0 trova automaticamente la dashboard sulla rete

---

## 🛠️ Stack tecnologico

| Componente | Tecnologia |
|-----------|-----------|
| Backend | Python 3.10+ · Flask |
| Database | SQLite |
| AI | Groq API (llama-3.3-70b) |
| Frontend | Bootstrap 5 · JavaScript |
| Hardware | fischertechnik TXT 4.0 |
| Comunicazione | HTTP POST · UDP broadcast |

---

## 📁 Struttura progetto

```
sorting-dashboard/
├── app.py                  # Flask app principale
├── discovery.py            # Auto-discovery IP sulla rete
├── simulate_demo.py        # Simulazione 10 pezzi per demo
├── setup.bat               # Installer Windows
├── setup.sh                # Installer Mac/Linux
├── requirements.txt        # Dipendenze Python
├── .env                    # Chiave API Groq (non in repo)
├── templates/
│   └── dashboard.html      # Dashboard web
└── txt40_files/            # File da caricare sul TXT 4.0
    ├── config.py           # Configurazione IP fallback
    ├── dashboard_client.py # Client HTTP con auto-discovery
    └── sorting_line.py     # Logica nastro + invio dati dashboard
```

---

## 🚀 Installazione

### Windows
```bat
setup.bat
```

### Mac / Linux
```bash
chmod +x setup.sh
./setup.sh
```

> ⚠️ Richiede **Python 3.10 o superiore**  
> Il setup verifica automaticamente la versione e suggerisce l'aggiornamento se necessario.

### Installazione manuale
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

---

## ⚙️ Configurazione

Crea un file `.env` nella cartella principale:

```
GROQ_API_KEY=la_tua_chiave_groq
```

Ottieni una chiave gratuita su [console.groq.com](https://console.groq.com)

---

## ▶️ Avvio

```bash
python app.py
```

Apri il browser su **http://localhost:5000**

> La dashboard è accessibile anche da altri PC sulla stessa rete:  
> `http://192.168.x.x:5000`

---

## 🔌 Integrazione TXT 4.0

### Setup hardware
- TXT 4.0 e PC sulla **stessa rete WiFi**
- L'IP viene trovato **automaticamente** via UDP broadcast — zero configurazione!

### File da caricare su ROBO Pro Coding
Copia i file dalla cartella `txt40_files/` nel progetto ROBO Pro Coding:

| File | Descrizione |
|------|-------------|
| `sorting_line.py` | Logica nastro con invio dati dashboard |
| `dashboard_client.py` | Client HTTP + auto-discovery |
| `config.py` | IP fallback (solo se auto-discovery non funziona) |

### Canali configurati

| Num | Colore | Esito | Passi encoder |
|-----|--------|-------|--------------|
| 1 | Bianco | PASSED | 11 |
| 3 | Blu | PASSED | 27 |
| altro | — | FAIL | 300 |

### Dati inviati alla dashboard (JSON)
```json
{
  "colore": "BLU",
  "bin": "Bin Blu",
  "passi_encoder": 27,
  "timestamp_inizio": "24/06/2026 10:35:00",
  "tempo_elaborazione": 2.3
}
```

---

## 📊 KPI monitorati

| KPI | Descrizione |
|-----|-------------|
| Totale pezzi | Numero totale di pezzi smistati nella sessione |
| Bianchi / Blu | Contatori per colore |
| Scarti | Pezzi non riconosciuti o FAIL |
| Accuracy | % pezzi smistati correttamente |
| T. medio | Tempo medio di elaborazione per pezzo (secondi) |
| Storico totale | Pezzi smistati in tutte le sessioni |

---

## 🤖 Assistente AI

L'assistente AI (powered by Groq) risponde in italiano a domande sulla produzione:

- *"Ci sono anomalie nella sessione corrente?"*
- *"Qual è l'accuracy di oggi?"*
- *"Quanti pezzi blu sono stati smistati?"*

---

## 🔮 Sviluppi futuri

- [ ] Integrazione lettore NFC per tracciabilità pezzi
- [ ] Supporto multi-nastro (EXT1/EXT2)
- [ ] Export report PDF/Excel
- [ ] Alert email in caso di troppi scarti
- [ ] Dashboard mobile responsive

---

## 📄 Licenza

Progetto didattico — uso libero con attribuzione.
