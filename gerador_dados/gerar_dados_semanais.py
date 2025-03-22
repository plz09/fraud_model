import pandas as pd
import numpy as np
from faker import Faker
from random import choices
from datetime import datetime
import os

fake = Faker('pt_BR')

def gerar_dados_semanais(num_linhas=50):
    """
    Gera exatamente 50 linhas, das quais 5 são fraudes, 
    cada uma com combinação distinta de (categoria, método).
    """

    # Definições de categorias e métodos com pesos para o 'resto' (não-fraude)
    categorias = ['Compra Online', 'Restaurante', 'Supermercado', 'Eletrônicos', 'Viagem']
    categoria_pesos = [0.3, 0.3, 0.25, 0.15, 0.1]

    metodos_pagamento = ['cartao_credito', 'cartao_debito', 'pix', 'boleto']
    metodo_pesos = [0.35, 0.3, 0.2, 0.1]

    # Monta dataset inicial (tudo não-fraude = 0)
    dados = []
    for _ in range(num_linhas):
        cat = choices(categorias, weights=categoria_pesos, k=1)[0]
        met = choices(metodos_pagamento, weights=metodo_pesos, k=1)[0]
        valor = round(np.random.uniform(10, 5000), 2)
        hora_transacao = fake.date_time_between(start_date='-7d', end_date='now')
        localizacao = fake.city()

        dados.append({
            'id_transacao': fake.unique.random_int(min=10000, max=99999),
            'valor': valor,
            'hora_transacao': hora_transacao,
            'categoria': cat,
            'metodo_pagamento': met,
            'localizacao': localizacao,
            'fraude': 0
        })

    df = pd.DataFrame(dados)

    # Agora forçamos 5 fraudes com combinações distintas
    # (Você pode trocar se quiser outras combinações)
    fraud_combos = [
        ("Compra Online", "pix"),
        ("Eletrônicos", "boleto"),
        ("Restaurante", "cartao_credito"),
        ("Viagem", "pix"),
        ("Supermercado", "cartao_debito")
    ]

    # Pegamos 5 índices aleatórios distintos (sem replacement)
    # mas garantindo que não haja repetição
    fraud_indices = df.sample(n=5, random_state=42).index

    # Aplica as 5 fraudes
    for i, idx in enumerate(fraud_indices):
        cat_fraude, met_fraude = fraud_combos[i]
        df.at[idx, 'categoria'] = cat_fraude
        df.at[idx, 'metodo_pagamento'] = met_fraude

        # Opcional: valores altos para a fraude
        # ou valores fora da curva dependendo da categoria
        if cat_fraude in ["Compra Online", "Eletrônicos", "Viagem"]:
            df.at[idx, 'valor'] = round(np.random.uniform(3000, 5000), 2)
        elif cat_fraude == "Supermercado":
            df.at[idx, 'valor'] = round(np.random.uniform(15, 60), 2)
        else:
            # Restaurante ou outro
            df.at[idx, 'valor'] = round(np.random.uniform(50, 2000), 2)

        df.at[idx, 'fraude'] = 1

    # Salva o CSV final
    os.makedirs('./dados/dados_semanais', exist_ok=True)
    data_atual = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    filename = f'./dados/dados_semanais/dados_semanais_{data_atual}.csv'
    df.to_csv(filename, index=False)
    print(f"✅ Gerados {num_linhas} registros, com 5 fraudes diversificadas, em {filename}")

if __name__ == "__main__":
    gerar_dados_semanais()
