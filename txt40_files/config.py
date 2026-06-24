"""
config.py — Configurazione dashboard per TXT 4.0
=================================================
Modifica SOLO questo file se hai problemi di connessione.
Normalmente l'IP viene trovato automaticamente!

Autore: Sebastiano Giaquinta
"""

# ── IP di fallback (usato solo se auto-discovery fallisce) ────
# Metti qui l'IP di NEBULA se sei a casa
# In aula viene trovato automaticamente!
FALLBACK_IP   = "192.168.1.45"
FALLBACK_PORT = 5000

# ── Timeout connessione (secondi) ─────────────────────────────
TIMEOUT = 2

# ── Porta discovery UDP ───────────────────────────────────────
DISCOVERY_PORT = 5001
