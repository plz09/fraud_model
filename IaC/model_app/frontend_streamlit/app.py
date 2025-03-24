import os
import streamlit as st
import requests
import pandas as pd
from sqlalchemy import create_engine

###################################################
# Decide se local ou AWS
###################################################
API_URL = "http://127.0.0.1:8000/prever"


DB_ENDPOINT = os.environ.get("DB_ENDPOINT", "localhost")
DB_NAME     = os.environ.get("DB_NAME", "db_fraudes")
DB_USER     = os.environ.get("DB_USER", "pellizzi")
DB_PASS     = os.environ.get("DB_PASS", "Pellizzi123!")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_ENDPOINT}:5432/{DB_NAME}"
engine = create_engine(DB_URL)

st.set_page_config(page_title="Detecção de Fraudes", layout="wide")

st.title("🔍 Sistema de Detecção de Fraudes")

aba = st.sidebar.radio("Navegação", ["Upload e Previsão", "📊 Dashboard Histórico"])

if aba == "Upload e Previsão":
    st.header("Upload de Arquivo CSV Semanal")
    uploaded_file = st.file_uploader("Faça upload do CSV semanal", type=["csv"])

    if uploaded_file:
        resposta = requests.post(API_URL, files={"arquivo": uploaded_file})

        if resposta.status_code == 200:
            df_resultado = pd.DataFrame(resposta.json()["resultado"])
            st.success("✅ Previsões realizadas com sucesso!")
            st.write(df_resultado)
            fraude_count = df_resultado["previsao_fraude"].sum()
            st.metric("Total de Transações", len(df_resultado))
            st.metric("Fraudes Detectadas", fraude_count)
        else:
            st.error(f"Erro na previsão. Status code: {resposta.status_code}")

elif aba == "📊 Dashboard Histórico":
    st.header("Dashboard Histórico de Previsões")

    try:
        df = pd.read_sql("SELECT * FROM previsoes_fraudes", con=engine)

        if df.empty:
            st.warning("Nenhuma previsão encontrada na tabela.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Transações", len(df))
            col2.metric("Fraudes Detectadas", df["previsao_fraude"].sum())

            ultima_data = df["data_envio"].max()
            col3.metric("Último Upload", ultima_data.strftime("%d/%m/%Y %H:%M") if ultima_data else "N/A")

            st.subheader("📌 Fraudes por Categoria")
            st.bar_chart(df[df["previsao_fraude"] == 1]["categoria"].value_counts())

            st.subheader("📈 Evolução por Data de Envio")
            df["data"] = df["data_envio"].dt.date
            st.line_chart(df.groupby("data")["previsao_fraude"].sum())

            st.subheader("📋 Histórico Completo")
            st.dataframe(df.sort_values("data_envio", ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
