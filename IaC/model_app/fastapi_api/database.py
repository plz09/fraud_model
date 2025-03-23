import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Caso o endpoint venha com "host:port", separamos
full_host = os.environ.get("DB_ENDPOINT", "localhost")
if ":" in full_host:
    DB_HOST, DB_PORT = full_host.split(":")
else:
    DB_HOST = full_host
    DB_PORT = "5432"

DB_USER = os.environ.get("DB_USER", "pellizzi")
DB_PASS = os.environ.get("DB_PASS", "Pellizzi123!")
DB_NAME = os.environ.get("DB_NAME", "db_fraudes")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
