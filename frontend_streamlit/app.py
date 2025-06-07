import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/prever"

st.set_page_config(page_title="Detecção de Fraudes", layout="wide")

st.title("🔍 Sistema de Detecção de Fraudes")

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

        # Download CSV gerado pela API (opcional: baseado na resposta da API)
        csv = df_resultado.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar resultado CSV", data=csv, file_name="previsoes.csv", mime="text/csv")

    else:
        st.error(f"Erro na previsão. Status code: {resposta.status_code}")
