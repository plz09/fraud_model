CREATE TABLE previsoes_fraudes (
    id SERIAL PRIMARY KEY,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_transacao INTEGER,
    valor FLOAT,
    hora_transacao TIMESTAMP,
    categoria VARCHAR(50),
    metodo_pagamento VARCHAR(50),
    localizacao VARCHAR(50),
    previsao_fraude INTEGER
);
