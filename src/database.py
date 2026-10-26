"""Conexión local; credenciales fuera del código."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
ROOT=Path(__file__).resolve().parents[1]
load_dotenv(ROOT/'.env')
def get_engine():
    return create_engine(URL.create('postgresql+psycopg2',
        username=os.environ['DB_USER'],password=os.environ['DB_PASSWORD'],
        host=os.getenv('DB_HOST','127.0.0.1'),port=int(os.getenv('DB_PORT','55433')),
        database=os.environ['DB_NAME']),pool_pre_ping=True)
