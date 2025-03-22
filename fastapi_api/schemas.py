from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from database import Base
from sqlalchemy import Column, Integer, Float, String, TIMESTAMP

# Schema FastAPI
class ResultadoPrevisao(BaseModel):
    resultado: List[Dict[str, Any]]

# Modelo SQLAlchemy
class PrevisaoFraude(Base):
    __tablename__ = "previsoes_fraudes"

    id = Column(Integer, primary_key=True, index=True)
    data_envio = Column(TIMESTAMP, default=datetime.now)
    id_transacao = Column(Integer)
    valor = Column(Float)
    hora_transacao = Column(TIMESTAMP)
    categoria = Column(String(50))
    metodo_pagamento = Column(String(50))
    localizacao = Column(String(50))
    previsao_fraude = Column(Integer)
