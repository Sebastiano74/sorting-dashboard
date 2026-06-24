"""
discovery.py — Auto-discovery server
Gira insieme a Flask e manda broadcast UDP sulla rete locale
così il TXT 4.0 trova l'IP della dashboard automaticamente.

Autore: Sebastiano Giaquinta
"""

import socket
import threading
import time

DISCOVERY_PORT = 5001
DISCOVERY_MESSAGE = b"SORTING_DASHBOARD_HERE"
BROADCAST_INTERVAL = 3  # secondi


def get_local_ip():
    """Trova l'IP locale della macchina sulla rete."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def start_discovery_server():
    """
    Avvia il server UDP che risponde alle richieste di discovery del TXT 4.0.
    Il TXT 4.0 manda una richiesta broadcast e questo server risponde con l'IP.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', DISCOVERY_PORT))
    local_ip = get_local_ip()
    print(f"[DISCOVERY] Server avviato su {local_ip}:{DISCOVERY_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data == b"FIND_DASHBOARD":
                response = f"DASHBOARD:{local_ip}:5000".encode()
                sock.sendto(response, addr)
                print(f"[DISCOVERY] Risposto a {addr[0]} con IP {local_ip}")
        except Exception as e:
            print(f"[DISCOVERY] Errore: {e}")


def start_broadcast():
    """
    Manda broadcast periodico sulla rete — opzionale,
    utile se il TXT 4.0 non riesce a fare la richiesta attiva.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    local_ip = get_local_ip()
    message = f"DASHBOARD:{local_ip}:5000".encode()

    while True:
        try:
            sock.sendto(message, ('<broadcast>', DISCOVERY_PORT))
            time.sleep(BROADCAST_INTERVAL)
        except Exception as e:
            print(f"[BROADCAST] Errore: {e}")
            time.sleep(BROADCAST_INTERVAL)


def init_discovery():
    """Avvia discovery server e broadcast in thread separati."""
    t1 = threading.Thread(target=start_discovery_server, daemon=True)
    t2 = threading.Thread(target=start_broadcast, daemon=True)
    t1.start()
    t2.start()
    print(f"[DISCOVERY] IP locale: {get_local_ip()}")
