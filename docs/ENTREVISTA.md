# Decisões para discutir

O teste corresponde aos últimos 480 dos 2.400 registros. A regularização é selecionada entre 0,01, 1, 10 e 100 pelo MAE de validação. Após a seleção, o modelo pontual é refitado em 80% dos registros. O baseline usa a média desse mesmo período.

O modelo conformal é independente: alpha fixo em 1, treino nos primeiros 60%, calibração nos 20% seguintes e avaliação nos últimos 20%. Não há refit depois da calibração. A API serve apenas o modelo pontual; não associa o intervalo ao estimador errado.

## Demonstração

1. Execute o pipeline e compare MAE com baseline.
2. Abra o formulário e altere distância e chuva.
3. Mostre as fatias de erro e a cobertura conformal abaixo do alvo nominal.
4. Explique por que conhecer o preparo final observado causaria vazamento.

## Limitações

- Não há validação em entregas reais, custos reais, sazonalidade ou geografia.
- A cobertura conformal pressupõe permutabilidade; a mudança temporal pode violá-la.
- PSI baixo não exclui mudança na relação entre atributos e alvo.
- Álgebra linear própria serve ao pequeno problema educacional; bibliotecas consolidadas são preferíveis em escala.
- Não usar para promessas comerciais, despacho ou avaliação de trabalhadores.

## Próximo experimento

Comparar boosting e regressão quantílica, rodar múltiplas sementes, avaliar custos assimétricos e obter um holdout real autorizado.

Explique o código com suas próprias palavras e informe o uso de assistência de IA. Este repositório não representa trabalho realizado no iFood.
