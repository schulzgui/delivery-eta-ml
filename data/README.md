# Data card — Delivery ETA ML

**100% sintético; licença MIT.**

2.400 entregas fictícias, semente 42. Atributos: distância (0,5–12 km), **preparo estimado disponível antes da entrega** (7–35 min), chuva/pico binários e fila (0–8). Alvo: minutos de entrega. IDs usam SYN e cada linha possui `synthetic=True`.

Fórmula: `4 + 2,4*distância + 0,85*preparo + 5*chuva + 4*pico + 1,1*fila + ruído normal(0,4)`. Os últimos 20% recebem mais 1,8 minuto de mudança condicional. O índice temporal e o ID não são atributos. O gerador quase linear favorece o modelo linear.

Gerador: `src/eta_lab/data.py`. Semente base 42, sem dados externos, scraping, nomes de clientes ou operação real.

- Não há validação em entregas reais, custos reais, sazonalidade ou geografia.
- A cobertura conformal pressupõe permutabilidade; a mudança temporal pode violá-la.
- PSI baixo não exclui mudança na relação entre atributos e alvo.
- Álgebra linear própria serve ao pequeno problema educacional; bibliotecas consolidadas são preferíveis em escala.
- Não usar para promessas comerciais, despacho ou avaliação de trabalhadores.
