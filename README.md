# Validador de RNA (Grampo e Pseudonó)

Aplicação em Python e Streamlit para validação de cadeias de RNA em duas etapas sequenciais:

1. **Etapa 1 — Grampo (Autômato de Pilha determinístico):** verifica se a entrada pertence à linguagem livre de contexto $`L_1 = w\,\ell\,\bar{w}^R\#B_1.B_2.B_3.B_4`$, com $`\vert{}w\vert{} \ge 3`$, $`\vert{}\ell\vert{} \ge 4`$ e cada $`B_i \in \{A, C, G, U\}^+`$.
2. **Etapa 2 — Pseudonó (Autômato Linearmente Limitado determinístico):** executada somente quando o AP aceita, verifica se o trecho após `#` pertence à linguagem sensível ao contexto $`L_2 = x.y.\bar{x}^R.\bar{y}^R`$, com $`x, y \in \{A, C, G, U\}^+`$.

Cadeia de referência, aceita pelos dois módulos (26 caracteres): `GCAUCaaaaGAUGC#AC.GG.GU.CC`.

## Requisitos

Python 3.10 ou superior.

## Instalação

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux ou macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executar a aplicação

```bash
streamlit run app/streamlit_app.py
```

A aplicação abre em http://localhost:8501 e tem três abas:

- **Validador:** campo de cadeia, botões com os três cenários de integração e exemplos extras. Mostra a decisão, o rastreamento passo a passo do AP (estado, posição de leitura e pilha), o do ALL (estado, fita e cabeçote) e a derivação da GLC para cadeias aceitas pelo AP. Espaços nas pontas da cadeia são ignorados.
- **Autômatos e GLC:** produções da gramática e tabelas de transições do AP e do ALL.
- **Casos de teste:** executa agora cada cadeia de `dados/` e mostra entrada, decisão esperada, decisão obtida, regra verificada e resultado.

## Repetir os testes

```bash
python -m pytest -v
```

Todos os testes devem passar. Eles cobrem o alfabeto, o AP, o ALL, a gramática, o fluxo de duas etapas, os arquivos de dados e a interface (com `streamlit.testing`).

## Cenários de integração

| Cadeia | AP | ALL | Regra |
|---|---|---|---|
| `GCAUCaaaaGAUGC#AC.GG.GU.CC` | aceita | aceita | grampo válido e pseudonó válido |
| `GCAUCaaaaGAUGA#AC.GG.GU.CC` | rejeita | não executa | fecho `GAUGA` não é o complemento reverso de `GCAUC` |
| `GCAUCaaaaGAUGC#AC.GG.GU.GG` | aceita | rejeita | `GG` não é o complemento reverso de `GG` (esperado `CC`) |

Uma cadeia com símbolo fora do alfabeto (por exemplo, `X` ou espaço no meio) não chega a nenhum autômato; a aplicação informa o símbolo e a posição, como em `Símbolo 'X' na posição 23 não pertence ao alfabeto {#, ., A, C, G, U, a, c, g, u}`.

## Modelos formais

- **Alfabeto de entrada:** `A C G U` (haste, fecho e blocos), `a c g u` (laço), `#` e `.`. O laço em minúsculas deixa o AP determinístico. Pareamentos: A–U e C–G.
- **GLC G1:** `S -> H#B.B.B.B`; `H`, `I`, `K` impõem os três pares mínimos da haste, `J` gera os pares seguintes e `J -> L`; `L` é o laço de 4 ou mais letras; `B` é um bloco não vazio de bases. As produções completas estão na aba "Autômatos e GLC".
- **AP:** 17 estados (`q0` a `q16`), pilha com `Z0` e o complemento de cada base da haste, aceitação por estado final (`q16`) com a entrada consumida por inteiro. Cada transição consome um símbolo, então termina em no máximo n passos.
- **ALL:** 35 estados, fita `⊢ c1 … cn ⊣` com n células graváveis e dois marcadores fixos. Primeiro renumera os três separadores (①②③) e rejeita bloco vazio; depois pareia B1 com B3 e B2 com B4, marcando com `×` cada base pareada. A memória de trabalho cabe na fita e nos estados. Cada volta marca pelo menos duas células, então termina em O(n²) passos.
- **Determinismo:** os dois autômatos são determinísticos. Uma combinação sem transição definida rejeita a cadeia.
- **Classificação:** $`L_1`$ é livre de contexto e não é regular. $`L_2`$ não é livre de contexto, pois a interseção com `A⁺.C⁺.U⁺.G⁺` resulta em $`\{A^n.C^m.U^n.G^m\}`$.

## Estrutura do repositório

```
app/streamlit_app.py            interface Streamlit
src/rna_validador/
  alfabeto.py                   alfabeto, complemento reverso e erro de símbolo inválido
  rastreamento.py               tipos de passo e de resultado
  automato_pilha.py             AP
  automato_limitado.py          ALL
  gramatica.py                  GLC e derivação mais à esquerda
  validador_duas_etapas.py      fluxo AP -> ALL
  conferencia.py                executa os arquivos de dados e compara com o esperado
dados/                          cadeias de teste (AP, ALL, integração e símbolos inválidos)
tests/                          testes com pytest
```

Todas as cadeias de `dados/` têm 18 ou mais caracteres.

## Limitações

- Os separadores `.` entre os blocos do pseudonó simplificam o ALL e não existem em RNA real.
- Não há pares G–U (oscilação) nem pseudonós de topologia geral; só o padrão `x.y.x̄ᴿ.ȳᴿ`.

## Equipe

| Integrante | Contribuição |
|---|---|
| João Pedro Silva | esqueleto do projeto, alfabeto, AP, GLC e derivação |
| Yago Patrick | ALL |
| Gabriel Miranda | fluxo de duas etapas e interface Streamlit |
| Carlos Eduardo | registros de teste, testes da interface e README |

## Referências

- Searls, D. B. "The Linguistics of DNA". *American Scientist*, 1992. Usa a hierarquia de Chomsky para classificar estruturas de DNA e RNA.
- Rivas, E.; Eddy, S. R. "A dynamic programming algorithm for RNA structure prediction including pseudoknots". *Journal of Molecular Biology*, 1999. Mostra que pseudonós ficam fora do alcance das gramáticas livres de contexto.
- Hopcroft, J. E.; Motwani, R.; Ullman, J. D. *Introduction to Automata Theory, Languages, and Computation*, cap. 7. Lema do bombeamento e fechamento das linguagens livres de contexto sob interseção com linguagens regulares.

## Uso de inteligência artificial

- **Ferramenta:** Claude Code (Anthropic).
- **Tarefas apoiadas:** planejamento do projeto e do modelo formal, escrita de código e testes, revisão de código.
- **O que a equipe verificou:** a equipe revisou os pull requests, executou a suíte de testes e a aplicação, e conferiu à mão as derivações e as cadeias de teste. Cada integrante deve conseguir explicar a parte que desenvolveu.
