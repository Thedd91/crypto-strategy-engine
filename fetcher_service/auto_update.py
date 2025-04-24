#!/usr/bin/env python3
"""
auto_update.py

Aggiorna ogni giorno i dati OHLCV delle crypto presenti nel DB,
riempiendo automaticamente eventuali gap dal database fino ad oggi.
"""

import logging
from datetime import datetime, timezone

from db import get_db_session
from fill_missing import fill_missing_for_coin
from sqlalchemy import text

# Setup log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_coin_list_from_db(session):
    """
    Restituisce una lista unica di coin_id presenti nella tabella OHLCV
    """
    result = session.execute(text("SELECT DISTINCT coin_id FROM ohlcv"))
    return [row[0] for row in result.fetchall()]


def main():
    logging.info("Avvio aggiornamento dati crypto dal DB")
    session = get_db_session()

    coin_list = get_coin_list_from_db(session)
    logging.info(f"{len(coin_list)} coin trovate nel DB")

    for coin_id in coin_list:
        try:
            logging.info(f"Inizio aggiornamento per {coin_id}")
            fill_missing_for_coin(session, coin_id, until=datetime.now(timezone.utc))
            logging.info(f"Completato {coin_id}")
        except Exception as e:
            logging.error(f"Errore aggiornando {coin_id}: {e}", exc_info=True)

    session.close()
    logging.info("Aggiornamento giornaliero completato")


if __name__ == "__main__":
    main()
