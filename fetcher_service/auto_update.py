#!/usr/bin/env python3
"""
auto_update.py

Aggiorna ogni giorno i dati OHLCV delle crypto presenti nel DB,
riempiendo automaticamente eventuali gap dal database fino ad oggi.
Salva anche il timestamp dell'ultimo aggiornamento nel DB.
"""

import logging
from datetime import datetime, timezone

from fetcher_service.db import get_db_session
from fetcher_service.fill_missing import fill_missing_for_coin
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

def update_last_updated(session):
    """
    Salva nel DB il timestamp dell'ultimo aggiornamento
    """
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    session.execute(
        text("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
    )
    session.execute(
        text("INSERT INTO meta (key, value) VALUES (:k, :v) ON CONFLICT (key) DO UPDATE SET value = :v"),
        {"k": "last_updated", "v": now_str}
    )
    session.commit()

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

    update_last_updated(session)
    session.close()
    logging.info("Aggiornamento giornaliero completato")

if __name__ == "__main__":
    main()
