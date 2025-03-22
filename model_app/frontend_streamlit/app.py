import streamlit as st
import requests
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

st.set_page_config(page_title="Detecção de Fraudes", layout="wide")

# Conexão com banco (ajuste para RDS futuramente)
DB_URL = "postgresql://pellizzi:Pellizzi123!@localhost:5432/db_fraudes"
engine = create_engine(DB_URL)

st.title("🔍 Sistema de Detecção de Fraudes")

aba = st.sidebar.radio("Navegação", ["Upload e Previsão", "📊 Dashboard Histórico"])

if aba == "Upload e Previsão":
    st.header("Upload de Arquivo CSV Semanal")
    uploaded_file = st.file_uploader("Faça upload do CSV semanal", type=["csv"])

    if uploaded_file:
        resposta = requests.post(
            "http://127.0.0.1:8000/prever", 
            files={"arquivo": uploaded_file}
        )

        if resposta.status_code == 200:
            resultado_json = resposta.json()
            df_resultado = pd.DataFrame(resultado_json["resultado"])

            st.success("✅ Previsões realizadas com sucesso!")
            st.write(df_resultado)

            fraude_count = df_resultado["previsao_fraude"].sum()
            total = len(df_resultado)
            st.metric("Total de Transações", total)
            st.metric("Fraudes Detectadas", fraude_count)
        else:
            st.error("Erro na previsão. Verifique a API.")

elif aba == "📊 Dashboard Histórico":
    st.header("Dashboard Histórico de Previsões")

    try:
        df = pd.read_sql("SELECT * FROM previsoes_fraudes", engine)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Transações", len(df))
        col2.metric("Fraudes Detectadas", df["previsao_fraude"].sum())
        col3.metric("Último Upload", df["data_envio"].max().strftime("%d/%m/%Y %H:%M"))

        st.subheader("📌 Fraudes por Categoria")
        st.bar_chart(df[df["previsao_fraude"] == 1]["categoria"].value_counts())

        st.subheader("📈 Evolução por Data de Envio")
        df["data"] = df["data_envio"].dt.date
        st.line_chart(df.groupby("data")["previsao_fraude"].sum())

        st.subheader("📋 Histórico Completo")
        st.dataframe(df.sort_values("data_envio", ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
