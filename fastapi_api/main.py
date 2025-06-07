from fastapi import FastAPI, UploadFile, File
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path

# Caminho do modelo
modelo_path = Path(__file__).resolve().parent.parent / "modelo_ml" / "modelo_treinado.pkl"
with open(modelo_path, "rb") as f:
    modelo = joblib.load(f)

app = FastAPI()

@app.get("/")
def root():
    return {"mensagem": "API de Fraudes rodando!"}

@app.post("/prever")
async def prever_fraudes(arquivo: UploadFile = File(...)):
    df = pd.read_csv(arquivo.file)

    # Pré-processamento
    df_encoded = pd.get_dummies(df, columns=['categoria', 'metodo_pagamento', 'localizacao'], drop_first=True)

    colunas_treino = modelo.feature_names_in_
    for col in colunas_treino:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_encoded = df_encoded[colunas_treino]

    # Previsão
    previsoes = modelo.predict(df_encoded)
    df['previsao_fraude'] = previsoes

    # Nome do arquivo de saída com base no nome do arquivo de entrada
    nome_entrada = Path(arquivo.filename).stem
    nome_arquivo = f"previsoes_{nome_entrada}.csv"

    # Salva o CSV no mesmo diretório do main.py
    saida_path = Path(__file__).resolve().parent / nome_arquivo
    df.to_csv(saida_path, index=False)

    return {"mensagem": "Previsão salva", "arquivo": nome_arquivo, "resultado": df.to_dict(orient="records")}
