from fastapi import FastAPI, UploadFile, File, Depends
import pandas as pd
import joblib
from sqlalchemy.orm import Session
from schemas import ResultadoPrevisao, PrevisaoFraude
from database import Base, SessionLocal, engine
from datetime import datetime

app = FastAPI()

# Carrega modelo
with open("../modelo_treinado.pkl", "rb") as f:
    modelo = joblib.load("../modelo_treinado.pkl")

# Cria tabela automaticamente
PrevisaoFraude.metadata.create_all(bind=engine)

# Dependência sessão DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"mensagem": "API de Fraudes rodando!"}

@app.post("/prever", response_model=ResultadoPrevisao)
async def prever_fraudes(arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(arquivo.file)

    df_encoded = pd.get_dummies(df, columns=['categoria', 'metodo_pagamento', 'localizacao'], drop_first=True)

    colunas_treino = modelo.feature_names_in_
    for col in colunas_treino:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_encoded = df_encoded[colunas_treino]

    previsoes = modelo.predict(df_encoded)
    df['previsao_fraude'] = previsoes

    # Salva no banco PostgreSQL
    for _, row in df.iterrows():
        previsao = PrevisaoFraude(
            id_transacao=int(row['id_transacao']),
            valor=row['valor'],
            hora_transacao=datetime.strptime(row['hora_transacao'], '%Y-%m-%d %H:%M:%S'),
            categoria=row['categoria'],
            metodo_pagamento=row['metodo_pagamento'],
            localizacao=row['localizacao'],
            previsao_fraude=int(row['previsao_fraude'])
        )
        db.add(previsao)
    db.commit()

    resultado = df.to_dict(orient='records')

    return {"resultado": resultado}
