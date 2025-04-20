# data_quality.py — Valuta la qualità dello storico per ciascuna coin nel DB
import pandas as pd
import psycopg2
from config import get_db_url
from datetime import datetime, timedelta

def get_quality_report():
    conn = psycopg2.connect(get_db_url())
    query = """
        SELECT timestamp::date AS date, symbol
        FROM public.market_data
        WHERE interval = 'daily'
        ORDER BY symbol, date;
    """
    df = pd.read_sql(query, conn)
    conn.close()

    results = []

    for symbol in df['symbol'].unique():
        symbol_df = df[df['symbol'] == symbol].copy()
        symbol_df['date'] = pd.to_datetime(symbol_df['date'])
        symbol_df = symbol_df.drop_duplicates(subset='date').sort_values('date')

        min_date = symbol_df['date'].min()
        max_date = symbol_df['date'].max()
        expected_days = (max_date - min_date).days + 1
        actual_days = symbol_df['date'].nunique()
        completeness = actual_days / expected_days if expected_days > 0 else 0

        # Calcola i gap (giorni mancanti)
        full_range = pd.date_range(start=min_date, end=max_date, freq='D')
        missing_days = full_range.difference(symbol_df['date']).size

        # Score qualitativo
        if completeness >= 0.95 and missing_days < 3:
            score = "Alta"
        elif completeness >= 0.80:
            score = "Media"
        else:
            score = "Bassa"

        results.append({
            "symbol": symbol,
            "inizio": min_date.date(),
            "fine": max_date.date(),
            "giorni_rilevati": actual_days,
            "periodo_totale": expected_days,
            "completezza": round(completeness * 100, 2),
            "missing_days": missing_days,
            "score": score
        })

    return pd.DataFrame(results)
