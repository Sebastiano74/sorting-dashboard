"""
sorting_line.py — Linea di smistamento AI
==========================================
Modificato da: Sebastiano Giaquinta
Basato su: Add_On_AI_modificato.ft (collega)

Modifiche:
  - Integrazione dashboard Flask via HTTP POST
  - Auto-discovery IP dashboard sulla rete
  - Log automatico di ogni pezzo smistato
  - Timestamp in formato europeo (DD/MM/YYYY)

Canali:
  num=1 → BIANCO → PASSED → posWHITE=11 passi
  num=3 → BLU    → PASSED → posBLUE=27  passi
  altro → FAIL   → fine nastro
"""

import time
from datetime import datetime
from fischertechnik.controller.Motor import Motor
from lib.controller import *
from lib.machine_learning import *
from dashboard_client import init_client, invia_evento

# ── Variabili globali ─────────────────────────────────────────
MovementSpeedCam = None
MovementSpeed    = None
posWHITE         = None
posBLUE          = None
posCam           = None
i                = None
posFinish        = None
num              = None
ts_inizio        = None
ts_start         = None


def thread_SLD():
    global MovementSpeedCam, MovementSpeed, posWHITE, posBLUE
    global posCam, i, posFinish, num, ts_inizio, ts_start

    print('[SLD] Avvio linea smistamento...')

    # Inizializza connessione dashboard
    init_client()

    # Parametri movimento
    MovementSpeedCam = 300
    MovementSpeed    = 512
    posWHITE         = 11
    posBLUE          = 27
    posCam           = 42
    posFinish        = 300
    num              = -1

    print('[SLD] Pronto — in attesa di pezzi...')

    while True:
        mainSLDexternal()


def moveRefM2():
    """Porta il deviatore M2 alla posizione di riferimento (finecorsa)."""
    global MovementSpeedCam, MovementSpeed, posWHITE, posBLUE
    global posCam, i, posFinish, num

    TXT_SLD_M_M2_encodermotor.set_speed(int(200), Motor.CW)
    TXT_SLD_M_M2_encodermotor.start()
    while True:
        if TXT_SLD_M_I2_mini_switch.is_closed():
            break
        time.sleep(0.010)
    TXT_SLD_M_M2_encodermotor.stop()


def mainSLDexternal():
    global MovementSpeedCam, MovementSpeed, posWHITE, posBLUE
    global posCam, i, posFinish, num, ts_inizio, ts_start

    if TXT_SLD_M_I1_photo_transistor.is_dark():

        # Salva timestamp ingresso pezzo
        ts_inizio = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ts_start  = time.time()

        moveRefM2()
        reset_inteface()
        print('[SLD] Pezzo rilevato — avvio ciclo')

        # Avanza nastro fino a liberare il sensore
        TXT_SLD_M_M1_encodermotor.set_speed(int(MovementSpeed * 0.5), Motor.CCW)
        TXT_SLD_M_M1_encodermotor.start_sync()
        for i in (0 <= posCam) and upRange(0, posCam, 1) or downRange(0, posCam, 1):
            if not TXT_SLD_M_I1_photo_transistor.is_dark():
                break
            time.sleep(0.01)
        TXT_SLD_M_M1_encodermotor.stop_sync()

        # Porta sotto la telecamera
        TXT_SLD_M_M1_encodermotor.set_speed(int(MovementSpeedCam), Motor.CCW)
        TXT_SLD_M_M1_encodermotor.set_distance(int(posCam))
        while True:
            if not TXT_SLD_M_M1_encodermotor.is_running():
                break
            time.sleep(0.010)

        print('[SLD] Posizione telecamera — analisi...')

        # Analisi AI + colore
        num = MakePictureRunKiReturnFoundPart()
        tempo = round(time.time() - ts_start, 2)

        if num == 1:
            # ── BIANCO PASSED ──
            print('[SLD] BIANCO — PASSED')
            TXT_SLD_M_M2_encodermotor.set_speed(int(300), Motor.CCW)
            TXT_SLD_M_M2_encodermotor.set_distance(int(posWHITE))
            while True:
                if not TXT_SLD_M_M2_encodermotor.is_running():
                    break
                time.sleep(0.010)
            TXT_SLD_M_M1_encodermotor.set_speed(int(MovementSpeed), Motor.CCW)
            TXT_SLD_M_M1_encodermotor.set_distance(int(posFinish))
            while True:
                if not TXT_SLD_M_M1_encodermotor.is_running():
                    break
                time.sleep(0.010)

            # Invia alla dashboard
            invia_evento(
                colore             = 'BIANCO',
                bin_dest           = 'Bin Bianco',
                passi              = posWHITE,
                timestamp_inizio   = ts_inizio,
                tempo_elaborazione = tempo,
            )

        elif num == 3:
            # ── BLU PASSED ──
            print('[SLD] BLU — PASSED')
            TXT_SLD_M_M2_encodermotor.set_speed(int(300), Motor.CCW)
            TXT_SLD_M_M2_encodermotor.set_distance(int(posBLUE))
            while True:
                if not TXT_SLD_M_M2_encodermotor.is_running():
                    break
                time.sleep(0.010)
            TXT_SLD_M_M1_encodermotor.set_speed(int(MovementSpeed), Motor.CCW)
            TXT_SLD_M_M1_encodermotor.set_distance(int(posFinish))
            while True:
                if not TXT_SLD_M_M1_encodermotor.is_running():
                    break
                time.sleep(0.010)

            # Invia alla dashboard
            invia_evento(
                colore             = 'BLU',
                bin_dest           = 'Bin Blu',
                passi              = posBLUE,
                timestamp_inizio   = ts_inizio,
                tempo_elaborazione = tempo,
            )

        else:
            # ── FAIL ──
            print('[SLD] FAIL — scarto')
            moveRefM2()
            TXT_SLD_M_M1_encodermotor.set_speed(int(MovementSpeed), Motor.CCW)
            TXT_SLD_M_M1_encodermotor.set_distance(int(posFinish))
            while True:
                if not TXT_SLD_M_M1_encodermotor.is_running():
                    break
                time.sleep(0.010)

            # Invia alla dashboard
            invia_evento(
                colore             = 'SCARTO',
                bin_dest           = 'Scarto',
                passi              = posFinish,
                timestamp_inizio   = ts_inizio,
                tempo_elaborazione = tempo,
            )


def upRange(start, stop, step):
    while start <= stop:
        yield start
        start += abs(step)


def downRange(start, stop, step):
    while start >= stop:
        yield start
        start -= abs(step)
