import os
from dotenv import load_dotenv

# Carica variabili da .env se presente
load_dotenv()

def get_db_url():
    return os.getenv("DATABASE_URL")
