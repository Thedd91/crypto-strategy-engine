# fetcher_service/db.py
# Connessione al database Neon e salvataggio dei dati

import pandas as pd
import psycopg2
from config import get_db_url

def save_ohlcv(df: pd.DataFrame, symbol: str):
    conn = psycopg2.connect(get_db_url())
    cursor = conn.cursor()
    for ts, row in df.iterrows():
        cursor.execute("""
            INSERT INTO market_data (timestamp, symbol, interval, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (ts, symbol, '1h', row['open'], row['high'], row['low'], row['close'], row['volume']))
    conn.commit()
    cursor.close()
    conn.close()
