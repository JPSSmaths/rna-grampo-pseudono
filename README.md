# Validador de RNA (Grampo e Pseudonó)

Aplicação em Python e Streamlit para validação de cadeias de RNA em duas etapas sequenciais:

1. **Etapa 1 — Grampo (Autômato de Pilha determinístico):** verifica se a entrada pertence à linguagem livre de contexto $L_1 = w\,\ell\,\bar{w}^R\#B_1.B_2.B_3.B_4$, com $\vert{}w\vert{} \ge 3$, $\vert{}\ell\vert{} \ge 4$ e cada $B_i \in \{A, C, G, U\}^+$.
2. **Etapa 2 — Pseudonó (Autômato Linearmente Limitado determinístico):** executada somente quando o AP aceita, verifica se o trecho após `#` pertence à linguagem sensível ao contexto $L_2 = x.y.\bar{x}^R.\bar{y}^R$, com $x, y \in \{A, C, G, U\}^+$.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt