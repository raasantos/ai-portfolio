# Tools Guide — IBOV Analysis & Recommendation Agent

Este guia explica cada uma das 7 tools: o que faz, por que existe como
tool separada, e o que já está implementado (reaproveitável). A schema
JSON e o handler de cada tool ficam para o Tutor escrever no Claude Code
— mas explicando o raciocínio antes de cada uma, não só entregando pronto
em silêncio. Use este guia como o roteiro de perguntas que o Tutor deve
percorrer com você antes de escrever cada tool, não como uma lista de
exercícios pra você resolver sozinho.

---

## Camada 1 — Fetch (dados reais, sem cálculo)

### 1. `fetch_price_history`

**O que faz:** busca a série histórica de preços (OHLCV) de um ticker.

**Por que é uma tool separada:** é a única forma do agente conseguir dado
de preço no sistema. Sem ela, nenhuma tool de compute técnico tem o que
processar.

**Já implementado:** `data_provider.py::BrapiClient.get_historical()`.
Você não escreve a chamada HTTP — você escreve o wrapper que:
1. Chama `get_historical()`
2. Guarda o resultado no cache do lado do servidor, indexado por ticker
3. Devolve pro modelo só uma confirmação resumida (ex: quantos pontos
   vieram, do dia X ao dia Y) — **nunca o array de preços inteiro**

**Perguntas que o Tutor deve discutir com você antes de escrever a schema:**
- O parâmetro `range` (1mo, 1y, etc.) deveria ter um default, ou o agente
  sempre precisa decidir explicitamente? Pense no trade-off: default
  esconde uma decisão; obrigar o agente a escolher toda vez gasta uma
  rodada de raciocínio a mais.
- O que a `description` da tool deveria dizer sobre QUANDO usá-la? (ex:
  "chame antes de qualquer tool de compute técnico, nunca depois")

---

### 2. `fetch_fundamental_statistics`

**O que faz:** busca P/L, Dividend Yield, P/VP de um ticker (endpoint
`statistics` da brapi).

**Por que é separada de `fetch_financial_data`:** são dois endpoints
diferentes na API real, com dados diferentes. Fundir as duas em uma tool
só esconderia essa diferença — e o agente perderia a chance de decidir
"preciso só de P/L, não preciso do resto" (embora nesse caso específico a
API sempre devolve tudo junto; a separação aqui é mais sobre modelagem
clara de domínio do que sobre economia de chamada).

**Já implementado:** `data_provider.py::BrapiClient.get_statistics()`.

**Pergunta que o Tutor deve discutir com você antes de escrever:** a tool deveria devolver os números crus
(trailingPE, dividendYield) direto, ou já formatados (ex: dividendYield
como percentual)? Lembra do item #1 do AUDIT_CHECKLIST — a unidade desse
campo é a suposição de maior risco do projeto. Decida isso DEPOIS de
verificar contra a API real (Fase 1), não antes.

---

### 3. `fetch_financial_data`

**O que faz:** busca ROE, dívida total, EBITDA (endpoint `financial-data`
da brapi).

**Já implementado:** `data_provider.py::BrapiClient.get_financial_data()`.

**Mesma lógica de design que `fetch_fundamental_statistics`.**

---

## Camada 2 — Compute (matemática determinística)

### 4. `compute_moving_average_crossover`

**O que faz:** calcula se a média móvel curta cruzou a longa, e se esse
cruzamento aconteceu no último ponto disponível.

**Por que recebe `ticker` e não `prices`:** essa é a regra central do
projeto. Se essa tool recebesse a lista de preços como parâmetro, o LLM
precisaria "ver" o array inteiro pra poder passá-lo de volta — e aí você
perde a garantia de que ele não está tentando interpretar a série sozinho.
Recebendo só `ticker`, a tool busca o preço no cache (que
`fetch_price_history` já populou) e devolve só o resultado.

**Já implementado:** a matemática está em
`indicators.py::moving_average_crossover_signal()`. Falta você escrever o
handler que: recebe `ticker` + `short_window` + `long_window`, busca os
preços do cache, chama a função, devolve o resultado.

**Pergunta que o Tutor deve discutir com você antes de escrever:** o que a tool devolve se
`fetch_price_history` nunca foi chamado pra esse ticker antes (cache
vazio)? Erro explícito, ou ela chama `fetch_price_history` sozinha por
baixo dos panos? A segunda opção parece conveniente, mas esconde do
agente uma decisão que deveria ser dele — pense em qual das duas respeita
melhor o princípio de Tool Selection genuína.

---

### 5. `compute_rsi`

**O que faz:** calcula RSI(period) pro ticker.

**Já implementado:** `indicators.py::rsi()`.

**Mesma lógica de cache que a tool 4.**

---

### 6. `compute_relative_volume`

**O que faz:** calcula o volume do último dia relativo à média dos N dias
anteriores.

**Já implementado:** `indicators.py::relative_volume()`.

**Pergunta que o Tutor deve discutir com você antes de escrever:** essa tool é sobre curto prazo (você
decidiu isso na sessão de design). A `description` deveria deixar isso
explícito pro agente, ou isso é uma coisa que o agente deveria inferir
sozinho a partir do contexto da conversa? Não tem resposta certa óbvia —
é uma chamada de design real.

---

### 7. `compute_debt_to_ebitda`

**O que faz:** calcula Dívida/EBITDA a partir dos dados já buscados por
`fetch_financial_data`.

**Por que essa e não as outras (P/L, ROE, DY) viram tool de compute:**
porque é a única que é DERIVADA — brapi não devolve Dívida/EBITDA
diretamente, você calcula a partir de `totalDebt` e `ebitda`. As outras
(P/L, DY, ROE) já vêm prontas da API, então não precisam de uma tool de
compute própria — só de extração, que já é o que `fetch_fundamental_statistics`
e `fetch_financial_data` fazem.

**Já implementado:** a fórmula está em
`fundamentals.py::extract_fundamentals()` (a parte que calcula
`debt_to_ebitda`). Você vai precisar decidir se reaproveita essa função
inteira ou extrai só o cálculo pra uma função nova mais enxuta — outra
decisão real de refatoração, não só "copiar e colar".

**Pergunta que o Tutor deve discutir com você antes de escrever:** essa tool depende de
`fetch_financial_data` já ter rodado. Isso é uma dependência entre tools —
como você comunica isso pro agente só através da `description`, sem
escrever um sistema de dependências explícito? (Essa pergunta especificamente
é sobre os limites do que dá pra fazer só com prompt engineering vs. o que
precisaria de controle de fluxo real — vale a pena sentir esse limite na
prática.)

---

## Depois de escrever as 7

Antes de passar pra Fase 3 (cache) e Fase 4 (loop), peça pro Tutor revisar
as 7 schemas juntas, lado a lado — não uma por vez isoladamente. Pergunta
pra fazer nesse ponto: olhando as 7 descriptions juntas, um agente que
nunca viu esse código conseguiria decidir corretamente qual chamar
primeiro, só lendo as descriptions? Se a resposta for "não tenho certeza",
as descriptions provavelmente precisam de mais uma rodada de ajuste antes
de testar de verdade.
