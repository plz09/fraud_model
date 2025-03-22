import pandas as pd
import numpy as np
from faker import Faker
from random import choice, random
from datetime import datetime

fake = Faker('pt_BR')

def gerar_dados_treino(num_linhas=1000):
    dados = []

    categorias = ['Compra Online', 'Restaurante', 'Supermercado', 'Eletrônicos', 'Viagem']
    metodos_pagamento = ['cartao_credito', 'cartao_debito', 'pix', 'boleto']

    for _ in range(num_linhas):
        valor = round(np.random.uniform(10, 5000), 2)
        hora_transacao = fake.date_time_between(start_date='-30d', end_date='now')
        categoria = choice(categorias)
        metodo_pagamento = choice(metodos_pagamento)
        localizacao = fake.city()

        # 10% das transações fraudulentas com características semelhantes às semanais
        if random() < 0.10:
            fraude = 1
            categoria = 'Compra Online'
            metodo_pagamento = 'pix'
            valor = round(np.random.uniform(3000, 5000), 2)
        else:
            fraude = 0

        dados.append({
            'id_transacao': fake.unique.random_int(min=10000, max=99999),
            'valor': valor,
            'hora_transacao': hora_transacao,
            'categoria': categoria,
            'metodo_pagamento': metodo_pagamento,
            'localizacao': localizacao,
            'fraude': fraude
        })

    df = pd.DataFrame(dados)
    df.to_csv('./dados/dados_treino.csv', index=False)
    print("Dados de treino atualizados gerados em ./dados/dados_treino.csv")

if __name__ == "__main__":
    gerar_dados_treino()
