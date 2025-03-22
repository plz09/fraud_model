import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Caso você queira rodar localmente e não setar variáveis de ambiente,
# definiremos defaults para localhost.
DB_ENDPOINT = os.environ.get("DB_ENDPOINT", "localhost")   # se não existir, assume localhost
DB_USER     = os.environ.get("DB_USER", "pellizzi")
DB_PASS     = os.environ.get("DB_PASS", "Pellizzi123!")
DB_NAME     = os.environ.get("DB_NAME", "db_fraudes")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_ENDPOINT}:5432/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
