import pandas as pd
import numpy as np
from faker import Faker
from random import choices
from datetime import datetime
import os

fake = Faker('pt_BR')

def gerar_dados_semanais(num_linhas=50):
    """
    Gera 50 linhas, das quais ~10 (20%) terão combinações 'suspeitas' 
    para diversificar categorias e métodos.
    """
    # Categorias e pesos
    categorias = ['Compra Online', 'Restaurante', 'Supermercado', 'Eletrônicos', 'Viagem']
    categoria_pesos = [0.3, 0.2, 0.25, 0.15, 0.1]  # soma = 1.0

    # Métodos e pesos
    metodos_pagamento = ['cartao_credito', 'cartao_debito', 'pix', 'boleto']
    metodo_pesos = [0.4, 0.3, 0.2, 0.1]  # soma = 1.0

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
            'localizacao': localizacao
            # Note: sem 'fraude'
        })

    df = pd.DataFrame(dados)

    # Selecione 5 índices aleatórios (10% de 50 = 5)
    num_suspeitas = 5
    suspeitas_indices = df.sample(n=num_suspeitas, random_state=42).index

    # Diversas combinações "suspeitas" para forçar
    combos_suspeitos = [
        ("Compra Online", "pix"),        
        ("Eletrônicos",   "boleto"),     
        ("Restaurante",   "cartao_credito"),  
        ("Viagem",        "pix"),        
        ("Supermercado",  "cartao_debito")   
    ]
    
    for i, idx in enumerate(suspeitas_indices):
        cat_suspeito, met_suspeito = combos_suspeitos[i]
        df.at[idx, 'categoria'] = cat_suspeito
        df.at[idx, 'metodo_pagamento'] = met_suspeito

        if cat_suspeito in ["Compra Online", "Eletrônicos", "Viagem"]:
            df.at[idx, 'valor'] = round(np.random.uniform(3000, 5000), 2)
        elif cat_suspeito == "Supermercado":
            df.at[idx, 'valor'] = round(np.random.uniform(10, 60), 2)
        else:
            df.at[idx, 'valor'] = round(np.random.uniform(50, 2000), 2)

    # Salva CSV 
    os.makedirs('./dados/dados_semanais', exist_ok=True)
    data_atual = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    filename = f'./dados/dados_semanais/dados_semanais_{data_atual}.csv'
    df.to_csv(filename, index=False)
    print(f"✅ Gerados {num_linhas} registros (com 5 suspeitos) em {filename}")

if __name__ == "__main__":
    gerar_dados_semanais(50)
