# Build Plan — IBOV Analysis & Recommendation Agent (v2)

Revisão pós-sessão: a v1 (`screener.py` + `synthesis.py` como pipeline fixo)
está superada pela decisão de construir um agente dinâmico de verdade.
Os arquivos da v1 continuam no repo como referência de comparação — ver
nota no final.

## Objetivos (os dois, não só um)

**Objetivo funcional:** ter um agente que analisa papéis do IBOV combinando
leitura técnica e fundamentalista, com recomendação sintetizada.

**Objetivo de aprendizado (o que estava faltando no plano anterior):**
aplicar de forma prática os conceitos do Capítulo 6 — Agents que você já
leu. Cada fase abaixo está amarrada a uma seção específica do capítulo,
pra você conseguir checar, ao final, se realmente aprendeu o conceito ou só
copiou um padrão.

| Seção do Cap 6 (já lida) | Onde aparece neste projeto |
|---|---|
| Tools | Escrever as 7 schemas de tool à mão (Camada Fetch + Camada Compute) |
| Function Calling | O loop real de múltiplas chamadas (não uma passada só) |
| Planning Granularity | A própria decisão de separar fetch de compute em tools distintas |
| Foundation Models as Planners / Plan Generation | O agente decidindo, a cada ticker, quais das 7 tools chamar |
| Complex Plans (control flow) | Ex: só chamar fundamentals se a leitura técnica já não descartou o papel |
| Tool Selection | Auditar se o agente escolhe as tools certas, ou se pula/repete sem necessidade |
| Reflection and Error Correction | Passo opcional de o agente conferir se tem dado suficiente antes de concluir |
| Failure Modes & Evaluation | O `AUDIT_CHECKLIST.md` ampliado (ver abaixo) |

**Seção ainda não lida:** Memory. Não vou fingir que este projeto já
aplica isso. Fica como gancho natural: depois de ler Memory, uma extensão
óbvia é o agente lembrar screenings anteriores entre sessões, em vez de
recomputar tudo do zero toda vez.

## Arquitetura final

```
Tutor (não é código — é um system prompt pro Claude Code, ver TUTOR_PROMPT.md)
  ↓ guia a sessão de construção

Agente único de Análise & Recomendação (dinâmico, com planning real)
  Tool box (7 tools, ver TOOLS_GUIDE.md):
    Fetch:    fetch_price_history, fetch_fundamental_statistics, fetch_financial_data
    Compute:  compute_moving_average_crossover, compute_rsi,
              compute_relative_volume, compute_debt_to_ebitda
  ↓ decide o que chamar, em que ordem, quando parar
  ↓ produz leitura técnica + fundamentalista + recomendação sintetizada
```

Regra de dado: as tools de Compute recebem só `ticker` (não array de
preço), e buscam o dado num cache do lado do servidor. O LLM nunca vê
preço bruto — só resultado já calculado. Essa regra não mudou desde a
decisão original desta sessão; só mudou COMO ela é aplicada (agora dentro
de um loop de tool-calling real, não uma pipeline de uma passada).

## O que já existe e é reaproveitável (não precisa reconstruir)

- `data_provider.py` — cliente HTTP real da brapi.dev, testado contra os
  nomes de campo reais da documentação
- `indicators.py` — indicadores técnicos escritos à mão, 5 testes passando
- `fundamentals.py` — extração + filtro fundamentalista, testado contra os
  exemplos reais da doc da brapi (WEGE3)
- `universe.py` — universo de tickers (sandbox → IBOV completo)
- `test_screener.py` — 11 testes formais, todos passando offline

Esses módulos viram a IMPLEMENTAÇÃO por trás das 7 tools. Você não
reescreve o cálculo de RSI — você escreve a tool schema que expõe
`indicators.rsi()` pro agente, e o handler que conecta os dois.

## O que fica superado (v1, mantido só como referência)

- `screener.py` — pipeline fixo, sempre roda tudo em ordem fixa
- `synthesis.py` — uma única chamada de LLM sem tool access
- `main.py` — orquestrador da v1

Não apague esses três arquivos. Depois que o agente dinâmico estiver
funcionando, vale rodar os dois lado a lado contra os mesmos 4 tickers e
comparar: o agente dinâmico chama menos tools quando os dados já bastam?
Ele erra em algum caso que o pipeline fixo acertava por força bruta? Essa
comparação empírica é o tipo de pergunta que a seção de Tool Selection
pede pra você fazer, não só ler.

## Fases (revisadas para a arquitetura v2)

### Fase 0 — Setup (Claude Code)
Igual ao plano anterior: git init, venv, `.env`, rodar
`pytest test_screener.py -v` (deve passar 11/11 sem tocar em rede).

### Fase 1 — Verificação contra API real
Igual ao plano anterior — item #1 do `AUDIT_CHECKLIST.md` continua sendo
a prioridade zero, independente da arquitetura.

### Fase 2 — Escrever as 7 tool schemas (com o Tutor)
Ler `TOOLS_GUIDE.md`, escrever cada schema você mesmo, uma de cada vez.
O Tutor audita cada uma antes de você seguir pra próxima — não é pra
escrever as 7 de uma vez e revisar no fim.

### Fase 3 — Implementar o cache do lado do servidor
Decisão de design pendente pra você resolver no Claude Code: cache em
memória (dict simples, válido só durante a execução) ou algo persistente?
Pra esse estágio, cache em memória basta — persistência é conversa pra
depois de ler Memory.

### Fase 4 — Loop de function calling real (multi-turno)
Diferente do Agent 1 (uma chamada, um plano, executa): aqui o agente pode
chamar uma tool, ver o resultado, decidir chamar outra, até decidir que
tem informação suficiente. Isso é o loop de verdade descrito na seção de
Function Calling — vale reler antes de implementar.

### Fase 5 — Rodar contra os 4 tickers sandbox, auditar
Usar o `AUDIT_CHECKLIST.md` ampliado (seção nova: riscos específicos de
agente dinâmico — loop infinito, chamadas redundantes, tool selection
inconsistente entre tickers parecidos).

### Fase 6 — Comparação empírica v1 (pipeline fixo) vs v2 (agente dinâmico)
Ver nota acima. Isso vira, inclusive, um ótimo post de LinkedIn técnico se
quiser documentar o aprendizado — mas isso é decisão sua, não vou puxar
pra esse assunto agora.

### Fase 7 — Plano pago + IBOV completo + publicação
Igual ao plano anterior (Fases 4-5 do plano v1).

## Arquivos desta sessão

```
ibov_screener/
├── (reaproveitáveis, já testados)
│   ├── data_provider.py
│   ├── indicators.py
│   ├── fundamentals.py
│   ├── universe.py
│   └── test_screener.py
├── (v1, superados, mantidos para comparação empírica na Fase 6)
│   ├── screener.py
│   ├── synthesis.py
│   └── main.py
├── (novos, para guiar a construção v2 no Claude Code)
│   ├── TUTOR_PROMPT.md
│   ├── TOOLS_GUIDE.md
│   └── BUILD_PLAN.md (este arquivo)
├── AUDIT_CHECKLIST.md
├── README.md
├── requirements.txt
└── .env.example
```
