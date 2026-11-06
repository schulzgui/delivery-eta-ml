# Model card — ETA ridge

Uso pretendido: demonstração de regressão, avaliação temporal e incerteza sobre dados sintéticos. Não suportado: despacho real, penalização de trabalhadores, promessa de entrega, inferência de comportamento de clientes.

Características: distância, preparo estimado, chuva, pico, fila. Sem ID ou índice temporal entre atributos. O estimador padroniza usando apenas os dados recebidos por `fit`. Regularização selecionada em 20% de validação; modelo pontual refitado nos primeiros 80%; últimos 20% reservados ao teste. Baseline é a média dos primeiros 80%.

Intervalo conformal: modelo separado treinado em 60%, alpha=1 fixo, resíduos absolutos em 20%, quantil corrigido pelo tamanho da amostra; teste final mede cobertura. Sob mudança temporal, a hipótese de permutabilidade não é garantida. Não há alegação de garantia de cobertura futura. API retorna só previsão pontual para evitar associar o intervalo ao estimador errado.

Monitoramento: PSI por atributo entre treino e teste; bins definidos no treino, suavização 0,5. Mudança condicional no alvo pode existir com PSI baixo. Acompanhar também MAE, cobertura e erro por fatia com rótulos atrasados.

O modelo favorece o gerador quase linear usado neste laboratório. Qualquer desempenho sobre entregas reais continua desconhecido. Pesos disponíveis em `artifacts/eta_model.json`; procedência em `artifacts/manifest.json`.
