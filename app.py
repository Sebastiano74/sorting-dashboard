"""
app.py — Sorting Line Dashboard
Autore  : Sebastiano Giaquinta
GitHub  : github.com/Sebastiano74
Stack   : Flask + SQLite + Groq AI
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

app = Flask(__name__)
DB_PATH = 'sorting.db'
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inizio TEXT NOT NULL,
            fine   TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS eventi (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            sessione_id         INTEGER NOT NULL,
            timestamp_inizio    TEXT NOT NULL,
            timestamp_fine      TEXT,
            tempo_elaborazione  REAL DEFAULT 0,
            colore              TEXT NOT NULL,
            bin                 TEXT NOT NULL,
            passi_encoder       INTEGER DEFAULT 0,
            FOREIGN KEY (sessione_id) REFERENCES sessioni(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

sessione_corrente = None

def avvia_sessione():
    global sessione_corrente
    conn = get_db()
    cur = conn.execute(
        'INSERT INTO sessioni (inizio) VALUES (?)',
        (datetime.now().strftime("%d/%m/%Y %H:%M:%S"),)
    )
    sessione_corrente = cur.lastrowid
    conn.commit()
    conn.close()
    return sessione_corrente

avvia_sessione()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/evento', methods=['POST'])
def ricevi_evento():
    dati = request.json
    conn = get_db()
    conn.execute('''
        INSERT INTO eventi 
        (sessione_id, timestamp_inizio, timestamp_fine, tempo_elaborazione, colore, bin, passi_encoder)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        sessione_corrente,
        dati.get('timestamp_inizio', datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        dati.get('tempo_elaborazione', 0),
        dati.get('colore', 'SCONOSCIUTO'),
        dati.get('bin', '?'),
        dati.get('passi_encoder', 0),
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/eventi')
def get_eventi():
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM eventi WHERE sessione_id = ? ORDER BY id DESC LIMIT 50',
        (sessione_corrente,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/kpi')
def get_kpi():
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM eventi WHERE sessione_id = ?',
        (sessione_corrente,)
    ).fetchall()
    eventi = [dict(r) for r in rows]
    totale   = len(eventi)
    bianchi  = len([e for e in eventi if e['colore'] == 'BIANCO'])
    blu      = len([e for e in eventi if e['colore'] == 'BLU'])
    scarti   = len([e for e in eventi if e['colore'] == 'SCARTO'])
    tempi    = [e['tempo_elaborazione'] for e in eventi if e['tempo_elaborazione'] > 0]
    t_medio  = round(sum(tempi) / len(tempi), 2) if tempi else 0
    accuracy = round((totale - scarti) / totale * 100, 1) if totale > 0 else 0
    tot_storico = conn.execute('SELECT COUNT(*) FROM eventi').fetchone()[0]
    conn.close()
    return jsonify({
        'sessione_id' : sessione_corrente,
        'totale'      : totale,
        'bianchi'     : bianchi,
        'blu'         : blu,
        'scarti'      : scarti,
        't_medio'     : t_medio,
        'accuracy'    : accuracy,
        'tot_storico' : tot_storico,
    })

@app.route('/api/storico')
def get_storico():
    conn = get_db()
    rows = conn.execute('''
        SELECT s.id, s.inizio, s.fine,
               COUNT(e.id) as totale,
               SUM(CASE WHEN e.colore='BIANCO' THEN 1 ELSE 0 END) as bianchi,
               SUM(CASE WHEN e.colore='BLU'    THEN 1 ELSE 0 END) as blu,
               SUM(CASE WHEN e.colore='SCARTO' THEN 1 ELSE 0 END) as scarti
        FROM sessioni s
        LEFT JOIN eventi e ON e.sessione_id = s.id
        GROUP BY s.id
        ORDER BY s.id DESC
        LIMIT 10
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/nuova_sessione', methods=['POST'])
def nuova_sessione():
    conn = get_db()
    conn.execute(
        'UPDATE sessioni SET fine=? WHERE id=?',
        (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), sessione_corrente)
    )
    conn.commit()
    conn.close()
    avvia_sessione()
    return jsonify({'status': 'ok', 'sessione_id': sessione_corrente})

@app.route('/api/ai', methods=['POST'])
def ai_analisi():
    domanda = request.json.get('domanda', '')
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM eventi WHERE sessione_id = ?',
        (sessione_corrente,)
    ).fetchall()
    conn.close()
    eventi  = [dict(r) for r in rows]
    totale  = len(eventi)
    bianchi = len([e for e in eventi if e['colore'] == 'BIANCO'])
    blu     = len([e for e in eventi if e['colore'] == 'BLU'])
    scarti  = len([e for e in eventi if e['colore'] == 'SCARTO'])
    accuracy = round((totale - scarti) / totale * 100, 1) if totale > 0 else 0

    contesto = f"""
Sei un assistente per una linea di smistamento industriale fischertechnik.
Dati sessione corrente:
- Totale pezzi: {totale}
- Bianchi: {bianchi}
- Blu: {blu}
- Scarti: {scarti}
- Accuracy: {accuracy}%
Rispondi in italiano in modo conciso e professionale.
"""
    risposta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": contesto},
            {"role": "user",   "content": domanda}
        ]
    )
    return jsonify({'risposta': risposta.choices[0].message.content})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
