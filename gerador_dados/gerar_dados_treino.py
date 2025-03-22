import pandas as pd
import numpy as np
from faker import Faker
from random import random, choices
from datetime import datetime

fake = Faker('pt_BR')

def gerar_dados_treino(num_linhas=1000):
    # categorias e métodos
    categorias = [
        'Compra Online', 'Restaurante', 'Supermercado',
        'Eletrônicos', 'Viagem', 'Farmacia', 'PetShop'
    ]
    cat_pesos = [0.15, 0.1, 0.1, 0.3, 0.15, 0.25, 0.05]  

    metodos_pagamento = [
        'cartao_credito', 'cartao_debito', 'pix',
        'boleto', 'paypal', 'bitcoin'
    ]
    met_pesos = [0.25, 0.25, 0.02, 0.15, 0.1, 0.05]       

    # Lista de combos suspeitos (fraude)
    # Cada item: (categoria, metodo, (valor_min, valor_max))
    combos_fraude = [
        ("Compra Online",  "cartao_credito",    (3000, 5000)),
        ("Eletrônicos",    "boleto",            (3000, 5000)),
        ("Eletrônicos",    "cartao_debito",     (300, 5000)),
        ("Viagem",         "bitcoin",           (3500, 5000)),
        ("Restaurante",    "cartao_credito",    (500, 3000)),
        ("Farmacia",       "cartao_credito",    (10, 5000)),
        ("Farmacia",       "pix",               (10, 5000)),
        ("PetShop",        "boleto",            (10, 500)),
        ("PetShop",        "pix",               (10, 5000))
        
    ]

    dados = []
    for _ in range(num_linhas):
        # Gera valores aleatórios para a maioria (não-fraude)
        cat = choices(categorias, cat_pesos, k=1)[0]
        met = choices(metodos_pagamento, met_pesos, k=1)[0]
        valor = round(np.random.uniform(10, 5000), 2)
        hora_transacao = fake.date_time_between(start_date='-30d', end_date='now')
        localizacao = fake.city()
        fraude = 0

        # ~30% de chance de ser fraude
        if random() < 0.30:
            fraude = 1
            # Escolhe aleatoriamente um combo suspeito
            combo = choices(combos_fraude, k=1)[0]
            cat, met, (vmin, vmax) = combo
            valor = round(np.random.uniform(vmin, vmax), 2)

        dados.append({
            'id_transacao': fake.unique.random_int(min=10000, max=99999),
            'valor': valor,
            'hora_transacao': hora_transacao,
            'categoria': cat,
            'metodo_pagamento': met,
            'localizacao': localizacao,
            'fraude': fraude
        })

    df = pd.DataFrame(dados)
    df.to_csv('./dados/dados_treino.csv', index=False)
    print("✅ Dados de treino atualizados gerados em ./dados/dados_treino.csv")

if __name__ == "__main__":
    gerar_dados_treino()
