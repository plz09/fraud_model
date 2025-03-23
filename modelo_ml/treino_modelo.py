import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import joblib

def carregar_dados(caminho_csv):
    df = pd.read_csv(caminho_csv, parse_dates=['hora_transacao'])
    return df

def pre_processamento(df):
    df_encoded = pd.get_dummies(df, columns=['categoria', 'metodo_pagamento', 'localizacao'], drop_first=True)
    X = df_encoded.drop(['id_transacao', 'fraude', 'hora_transacao'], axis=1)
    y = df_encoded['fraude']
    return X, y

def treinar_e_salvar_modelo(csv_path):
    df = carregar_dados(csv_path)
    X, y = pre_processamento(df)

    # Divisão em treino e teste 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    modelo = RandomForestClassifier(random_state=42)
    modelo_treinado = modelo.fit(X_train, y_train)

    # Avaliação do modelo
    y_pred = modelo_treinado.predict(X_test)
    print("Relatório de classificação:\n", classification_report(y_test, y_pred))
    print("Matriz de confusão:\n", confusion_matrix(y_test, y_pred))

    # Salva o modelo treinado
    with open('modelo_treinado.pkl', 'wb') as f:
        joblib.dump(modelo_treinado, '../Iac/model_app/modelo_treinado.pkl')


    print("✅ Modelo treinado e salvo com sucesso em modelo_treinado.pkl")

if __name__ == "__main__":
    caminho_csv = "../gerador_dados/dados/dados_treino.csv"
    treinar_e_salvar_modelo(caminho_csv)
