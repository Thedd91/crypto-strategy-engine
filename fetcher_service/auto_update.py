#!/usr/bin/env python3
"""
auto_update.py

Script per aggiornare ogni giorno i dati OHLCV delle crypto,
riempiendo automaticamente eventuali gap dal database fino ad oggi.
"""

import logging
from datetime import datetime, timezone

from db import get_db_session
from fill_missing import fill_missing_for_coin
from config import COIN_LIST  # definisci in config.py la lista dei coin da aggiornare

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def main():
    logging.info("Avvio aggiornamento dati crypto")
    session = get_db_session()

    for coin_id in COIN_LIST:
        try:
            logging.info(f"Inizio fill_missing per {coin_id}")
            fill_missing_for_coin(session, coin_id, until=datetime.now(timezone.utc))
            logging.info(f"Completato aggiornamento per {coin_id}")
        except Exception as e:
            logging.error(f"Errore aggiornando {coin_id}: {e}", exc_info=True)

    session.close()
    logging.info("Aggiornamento giornaliero completato")

if __name__ == "__main__":
    main()
