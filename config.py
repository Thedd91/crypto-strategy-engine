# fetcher_service/config.py
# Gestione configurazioni da .env

import os
from dotenv import load_dotenv

load_dotenv()

def get_db_url():
    return os.getenv("DATABASE_URL")
