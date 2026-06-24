"""
dashboard_client.py — Client HTTP per la dashboard
===================================================
Gestisce la connessione alla dashboard Flask con auto-discovery.
Il TXT 4.0 trova automaticamente l'IP della dashboard sulla rete.

Autore: Sebastiano Giaquinta
"""

import socket
import time
import threading
from datetime import datetime
from config import FALLBACK_IP, FALLBACK_PORT, TIMEOUT, DISCOVERY_PORT

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False
    print("[CLIENT] requests non disponibile — dashboard disabilitata")

# ── Stato connessione ─────────────────────────────────────────
_dashboard_url = None
_connected     = False
_lock          = threading.Lock()


def _find_dashboard_ip():
    """
    Cerca la dashboard sulla rete locale via UDP broadcast.
    Ritorna l'IP trovato o il FALLBACK_IP.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)

    try:
        # Manda richiesta broadcast
        sock.sendto(b"FIND_DASHBOARD", ('<broadcast>', DISCOVERY_PORT))
        data, addr = sock.recvfrom(1024)
        response = data.decode()

        if response.startswith("DASHBOARD:"):
            parts = response.split(":")
            ip   = parts[1]
            port = int(parts[2])
            print(f"[CLIENT] Dashboard trovata: {ip}:{port}")
            return ip, port

    except socket.timeout:
        print(f"[CLIENT] Auto-discovery timeout — uso fallback {FALLBACK_IP}:{FALLBACK_PORT}")
    except Exception as e:
        print(f"[CLIENT] Errore discovery: {e}")
    finally:
        sock.close()

    return FALLBACK_IP, FALLBACK_PORT


def init_client():
    """
    Inizializza il client — trova l'IP della dashboard automaticamente.
    Da chiamare all'avvio del programma sul TXT 4.0.
    """
    global _dashboard_url, _connected

    if not REQUESTS_OK:
        return

    print("[CLIENT] Ricerca dashboard sulla rete...")
    ip, port = _find_dashboard_ip()
    _dashboard_url = f"http://{ip}:{port}/evento"

    # Test connessione
    try:
        r = requests.get(f"http://{ip}:{port}/", timeout=TIMEOUT)
        if r.status_code == 200:
            _connected = True
            print(f"[CLIENT] ✓ Connesso alla dashboard: {_dashboard_url}")
        else:
            print(f"[CLIENT] Dashboard risponde ma con errore {r.status_code}")
    except Exception:
        print(f"[CLIENT] Dashboard non raggiungibile — continuo senza log")


def invia_evento(colore: str, bin_dest: str, passi: int,
                 timestamp_inizio: str = None, tempo_elaborazione: float = 0):
    """
    Invia un evento di smistamento alla dashboard.
    Se la dashboard non è raggiungibile, continua senza errori.

    Args:
        colore            : 'BIANCO', 'BLU' o 'SCARTO'
        bin_dest          : nome del bin (es. 'Bin Bianco')
        passi             : passi encoder usati
        timestamp_inizio  : quando è arrivato il pezzo (formato dd/mm/yyyy HH:MM:SS)
        tempo_elaborazione: secondi impiegati per elaborare
    """
    if not REQUESTS_OK or not _dashboard_url:
        return

    if timestamp_inizio is None:
        timestamp_inizio = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    payload = {
        'colore'            : colore,
        'bin'               : bin_dest,
        'passi_encoder'     : passi,
        'timestamp_inizio'  : timestamp_inizio,
        'tempo_elaborazione': round(tempo_elaborazione, 2),
    }

    def _send():
        try:
            requests.post(_dashboard_url, json=payload, timeout=TIMEOUT)
        except Exception:
            pass  # Non bloccare il nastro se la dashboard è offline

    # Manda in thread separato per non rallentare il nastro
    threading.Thread(target=_send, daemon=True).start()
