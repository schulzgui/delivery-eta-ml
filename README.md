# Delivery ETA ML

**Previsão de tempo de entrega com validação temporal, intervalos conformais e monitoramento de mudanças na distribuição.**

Guilherme Schulz · Portfólio técnico independente · Python 3.10+ · Licença MIT

> Todos os dados e políticas são sintéticos. Não há vínculo com o iFood, implantação empresarial ou impacto comercial medido. Projeto desenvolvido com assistência de IA; implementação, testes e limitações estão disponíveis para revisão.

## Problema e objetivo

Uma operação de entregas precisa estimar prazos e entender quando as previsões deixam de ser confiáveis. Este laboratório compara uma regressão com uma estimativa baseada na média histórica e avalia erros, incerteza e mudanças nos dados.

## O que está implementado

- Regressão ridge em Python puro, com padronização ajustada somente no treino.
- Seleção de regularização em validação temporal e teste separado.
- MAE, RMSE, P90 do erro e fatias por chuva/pico.
- Modelo separado para intervalos conformais calibrados por resíduos.
- PSI com bins definidos no treino e manifesto SHA256.
- API local com validação de faixa e formulário de previsão.

## Executar localmente

Este repositório é independente: não exige o monorepositório original nem os outros dois projetos. Não requer chave de API, serviço pago ou dependências Python de execução. Extraia o ZIP e abra um terminal na raiz de `delivery-eta-ml`.

macOS / Linux:

```bash
export PYTHONPATH=src
python3 -m eta_lab.cli run
python3 -m unittest discover -s tests -v
python3 -m eta_lab.cli serve
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m eta_lab.cli run
python -m unittest discover -s tests -v
python -m eta_lab.cli serve
```

Abra [a demo local](http://127.0.0.1:8001). Encerre com Ctrl+C. Para outra porta, use `serve --port 9000`. Execute na raiz do repositório; `--base CAMINHO` permite escolher outro diretório de dados/artefatos.

Opcional: `python3 -m pip install -e .` instala o comando `delivery-eta-ml`. Após a instalação, use `delivery-eta-ml run` ou `delivery-eta-ml serve`. A instalação requer obter o build backend se ele não estiver instalado; a execução por `PYTHONPATH` funciona sem esse passo.

## Arquitetura

```text
CSV sintético → treino 60% / validação 20% / teste 20% → seleção de alpha → refit nos primeiros 80% → modelo pontual
CSV sintético → treino 60% (alpha=1) / calibração 20% / teste 20% → intervalo conformal e cobertura
Treino versus teste → PSI por atributo → relatório
```

`eta.py`: ajuste e avaliação; `monitoring.py`: conformal e PSI; `data.py`: gerador.

## Método e avaliação

O teste corresponde aos últimos 480 dos 2.400 registros. A regularização é selecionada entre 0,01, 1, 10 e 100 pelo MAE de validação. Após a seleção, o modelo pontual é refitado em 80% dos registros. O baseline usa a média desse mesmo período.

O modelo conformal é independente: alpha fixo em 1, treino nos primeiros 60%, calibração nos 20% seguintes e avaliação nos últimos 20%. Não há refit depois da calibração. A API serve apenas o modelo pontual; não associa o intervalo ao estimador errado.

Resultados observados e contagens de testes: [relatório reproduzido](docs/RESULTADOS.md). Dados detalhados: [metrics.json](artifacts/metrics.json). Procedência: [manifest.json](artifacts/manifest.json).

O manifesto registra semente, Python e hashes SHA256 de dados e implementação. Não é uma assinatura criptográfica de autoria. O comando `run` sobrescreve os dados sintéticos e artefatos gerados no diretório escolhido.

## Dados e origem

2.400 entregas fictícias, semente 42. Atributos: distância (0,5–12 km), **preparo estimado disponível antes da entrega** (7–35 min), chuva/pico binários e fila (0–8). Alvo: minutos de entrega. IDs usam SYN e cada linha possui `synthetic=True`.

Fórmula: `4 + 2,4*distância + 0,85*preparo + 5*chuva + 4*pico + 1,1*fila + ruído normal(0,4)`. Os últimos 20% recebem mais 1,8 minuto de mudança condicional. O índice temporal e o ID não são atributos. O gerador quase linear favorece o modelo linear.

Leia o [data card](data/README.md). Os dados são distribuídos sob MIT, junto com o código.

## API local

| Método e rota      | Função                         |
| ------------------ | ------------------------------ |
| `GET /`            | Formulário de demonstração     |
| `GET /health`      | Verificação de disponibilidade |
| `GET /api/metrics` | Resultados da última execução  |
| `POST /api/eta`    | Executar a operação do projeto |

Com o servidor iniciado:

```bash
curl -X POST http://127.0.0.1:8001/api/eta \
  -H 'Content-Type: application/json' \
  -d '{"distance_km": 5, "prep_minutes": 20, "rain": 0, "peak": 1, "backlog": 3}'
```

A resposta é JSON. Entradas inválidas retornam HTTP 400, formato de conteúdo inadequado 415, origem incompatível 403 e rota desconhecida 404. Há limite de 8 KiB por corpo de requisição. A demo escuta apenas em `127.0.0.1`; não deve ser exposta à internet sem autenticação, TLS, servidor de produção e revisão de segurança.

## Testes e reprodução

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 scripts/verify_reproduction.py
```

O segundo comando compara dados gerados byte a byte e métricas/modelos JSON com tolerância numérica de `1e-10`, para acomodar arredondamento entre versões Python. A versão Python no manifesto pode variar. Os testes de integração iniciam a API em porta temporária e usam diretórios descartáveis. A CI está configurada para Python 3.10, 3.12 e 3.13; apenas os testes locais efetivamente executados são declarados no relatório.

## Estrutura

```text
src/eta_lab/      algoritmos, gerador, CLI e servidor
scripts/                 verificação dos artefatos versionados
tests/                   testes de domínio e integração HTTP
data/                    dados sintéticos e data card
artifacts/               métricas e manifesto de procedência
docs/                    resultados e roteiro técnico
.github/workflows/       CI por versão Python
```

## Demonstração para entrevista

1. Execute o pipeline e compare MAE com baseline.
2. Abra o formulário e altere distância e chuva.
3. Mostre as fatias de erro e a cobertura conformal abaixo do alvo nominal.
4. Explique por que conhecer o preparo final observado causaria vazamento.

Leia [o guia técnico](docs/ENTREVISTA.md) e reproduza o experimento antes de apresentá-lo. Declare claramente a contribuição da assistência de IA e as modificações que você revisou ou realizou.

## Limitações e decisões

- Não há validação em entregas reais, custos reais, sazonalidade ou geografia.
- A cobertura conformal pressupõe permutabilidade; a mudança temporal pode violá-la.
- PSI baixo não exclui mudança na relação entre atributos e alvo.
- Álgebra linear própria serve ao pequeno problema educacional; bibliotecas consolidadas são preferíveis em escala.
- Não usar para promessas comerciais, despacho ou avaliação de trabalhadores.

A inspeção visual da demo ainda não foi concluída; os endpoints são cobertos por testes HTTP. Nenhum resultado deste laboratório comprova experiência profissional no iFood.

## Próximos experimentos — ainda não implementados

Comparar boosting e regressão quantílica, rodar múltiplas sementes, avaliar custos assimétricos e obter um holdout real autorizado.

## Publicar como repositório separado

Crie um repositório vazio chamado `delivery-eta-ml` na sua conta. Envie **o conteúdo da raiz deste projeto**, incluindo arquivos ocultos, sem a pasta externa e sem o ZIP. Alternativamente:

```bash
git init -b main
git add .
git commit -m "Add standalone reproducible project"
git remote add origin https://github.com/SEU_USUARIO/delivery-eta-ml.git
git push -u origin main
```

Substitua `SEU_USUARIO` pelo seu login. Autenticação Git precisa estar configurada. Confirme a execução da aba Actions após o envio. Esses comandos não foram executados contra um novo repositório remoto nesta reorganização.

## Licença e contribuição

[MIT](LICENSE). Para propor alterações: descreva o problema, preserve a identificação sintética, execute os testes e regenere artefatos quando modificar dados ou algoritmos. Não atualize métricas manualmente para fazê-las parecer melhores.
