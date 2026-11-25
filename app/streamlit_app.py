from html import escape

import streamlit as st
from rna_validador.alfabeto import ALFABETO_ENTRADA
from rna_validador.automato_limitado import (
    DESCRICAO_DO_MOVIMENTO, ESTADOS as ESTADOS_DO_ALL, MARCA_PAREADA, TABELA_TRANSICOES as TRANSICOES_DO_ALL,
)
from rna_validador.automato_pilha import (
    ESTADOS as ESTADOS_DO_AP, FUNDO_DA_PILHA, QUALQUER_TOPO, TABELA_TRANSICOES as TRANSICOES_DO_AP,
)
from rna_validador.conferencia import ARQUIVOS_DE_DADOS, carregar_registros, conferir_registros
from rna_validador.gramatica import PRODUCOES
from rna_validador.validador_duas_etapas import (
    ACEITA, DESCRICAO_DA_DECISAO, ERRO_DE_ALFABETO, REJEITADA_NO_ALL, REJEITADA_NO_AP, ResultadoDuasEtapas,
    validar_em_duas_etapas,
)

CADEIA_DE_REFERENCIA = "GCAUCaaaaGAUGC#AC.GG.GU.CC"

EXEMPLOS_ADICIONAIS = {
    "Menor cadeia aceita": "ACGaaaaCGU#A.C.U.G",
    "Laço com 3 letras": "GCAUCaaaGAUGC#AC.GG.GU.CC",
    "Símbolo fora do alfabeto": "GCAUCaaaaGAUGC#AC.GG.GT.CC",
}

ROTULO_DO_CENARIO = {
    ACEITA: "Cenário 1 · aceita nos dois",
    REJEITADA_NO_AP: "Cenário 2 · rejeitada no AP",
    REJEITADA_NO_ALL: "Cenário 3 · rejeitada no ALL",
}

ESTILO = """
<style>
.fita { display: flex; flex-wrap: wrap; gap: 2px; margin: 0.4rem 0 0.8rem; font-family: ui-monospace, monospace; }
.celula { min-width: 1.7em; padding: 0.1em 0.2em; text-align: center; border: 1px solid rgba(128, 128, 128, 0.45);
          border-radius: 5px; font-size: 1.05rem; line-height: 1.2; }
.celula small { display: block; font-size: 0.62rem; opacity: 0.6; }
.celula.consumida { opacity: 0.4; }
.celula.marcada { background: rgba(46, 160, 67, 0.18); }
.celula.marcador { background: rgba(128, 128, 128, 0.15); }
.celula.atual { border: 2px solid #ff4b4b; background: rgba(255, 75, 75, 0.16); font-weight: 700; }
.celula.invalida { border: 2px solid #ff4b4b; background: rgba(255, 75, 75, 0.35); font-weight: 700; }
.cabecote { color: #ff4b4b; font-size: 0.7rem; display: block; height: 1em; }
.pilha { display: inline-flex; flex-direction: column; gap: 3px; font-family: ui-monospace, monospace; min-width: 4em; }
.pilha .celula { min-width: 3.5em; }
.pilha .topo { border: 2px solid #ff4b4b; font-weight: 700; }
.legenda { font-size: 0.8rem; opacity: 0.7; }
</style>
"""


def celula(simbolo: str, indice: int, classes: str = "", acima: str = "") -> str:
    return (
        f'<div class="celula {classes}"><span class="cabecote">{acima}</span>'
        f'{escape(simbolo)}<small>{indice}</small></div>'
    )


def desenhar_html(conteudo: str) -> None:
    st.markdown(conteudo, unsafe_allow_html=True)


def fita_da_entrada_do_ap(entrada: str, posicao: int) -> str:
    celulas = []
    for indice, simbolo in enumerate(entrada):
        if indice < posicao:
            classes = "consumida"
        elif indice == posicao:
            classes = "atual"
        else:
            classes = ""
        celulas.append(celula(simbolo, indice + 1, classes, "▼" if indice == posicao else ""))
    return f'<div class="fita">{"".join(celulas)}</div>'


def desenho_da_pilha(pilha: tuple[str, ...]) -> str:
    itens = []
    for altura, simbolo in reversed(list(enumerate(pilha))):
        classes = "topo" if altura == len(pilha) - 1 else ""
        itens.append(f'<div class="celula {classes}">{escape(simbolo)}</div>')
    return f'<div class="pilha">{"".join(itens)}</div>'


def fita_do_all(fita: tuple[str, ...], posicao_cabecote: int) -> str:
    celulas = []
    for indice, simbolo in enumerate(fita):
        eh_marcador = indice in (0, len(fita) - 1)
        if indice == posicao_cabecote:
            classes = "atual"
        elif eh_marcador:
            classes = "marcador"
        elif simbolo == MARCA_PAREADA:
            classes = "marcada"
        else:
            classes = ""
        celulas.append(celula(simbolo, indice, classes, "▼" if indice == posicao_cabecote else ""))
    return f'<div class="fita">{"".join(celulas)}</div>'


def entrada_com_simbolo_invalido(entrada: str, posicao_invalida: int) -> str:
    celulas = [
        celula(simbolo, indice + 1, "invalida" if indice + 1 == posicao_invalida else "")
        for indice, simbolo in enumerate(entrada)
    ]
    return f'<div class="fita">{"".join(celulas)}</div>'


def escolher_passo(rotulo: str, quantidade_de_passos: int, chave: str) -> int:
    if quantidade_de_passos <= 1:
        return 0
    return st.slider(rotulo, 0, quantidade_de_passos - 1, 0, key=chave)


def descrever_topo(topo) -> str:
    return "qualquer" if topo is QUALQUER_TOPO else topo


def mostrar_etapa_do_ap(resultado: ResultadoDuasEtapas) -> None:
    passos = resultado.resultado_ap.passos
    st.subheader("Etapa 1 · Autômato de pilha (grampo)")
    veredito = "aceitou" if resultado.resultado_ap.aceita else "rejeitou"
    st.write(f"O AP **{veredito}**: {resultado.resultado_ap.motivo}.")
    indice = escolher_passo("Passo do AP", len(passos), f"passo_ap::{resultado.entrada}")
    passo = passos[indice]
    coluna_da_entrada, coluna_da_pilha = st.columns([4, 1])
    with coluna_da_entrada:
        st.markdown(f"**Passo {indice} de {len(passos) - 1}** · estado `{passo.estado}` · posição de leitura {passo.posicao}")
        desenhar_html(fita_da_entrada_do_ap(resultado.entrada, passo.posicao))
        st.caption(passo.acao)
    with coluna_da_pilha:
        st.markdown("**Pilha** (topo em cima)")
        desenhar_html(desenho_da_pilha(passo.pilha))
    with st.expander("Rastreamento completo do AP"):
        st.dataframe(
            [
                {"passo": numero, "estado": item.estado, "posição": item.posicao,
                 "pilha (base → topo)": " ".join(item.pilha), "ação": item.acao}
                for numero, item in enumerate(passos)
            ],
            hide_index=True,
            width="stretch",
        )


def mostrar_etapa_do_all(resultado: ResultadoDuasEtapas) -> None:
    st.subheader("Etapa 2 · Autômato linearmente limitado (pseudonó)")
    if resultado.resultado_all is None:
        st.info("O ALL não foi executado, porque a cadeia não passou pela etapa 1.")
        return
    passos = resultado.resultado_all.passos
    veredito = "aceitou" if resultado.resultado_all.aceita else "rejeitou"
    st.write(
        f"Entrada do ALL: `{resultado.entrada_all}` (n = {len(resultado.entrada_all)} células graváveis). "
        f"O ALL **{veredito}**: {resultado.resultado_all.motivo}."
    )
    indice = escolher_passo("Passo do ALL", len(passos), f"passo_all::{resultado.entrada}")
    passo = passos[indice]
    st.markdown(f"**Passo {indice} de {len(passos) - 1}** · estado `{passo.estado}` · cabeçote na célula {passo.posicao_cabecote}")
    desenhar_html(fita_do_all(passo.fita, passo.posicao_cabecote))
    st.caption(passo.acao)
    desenhar_html(
        '<div class="legenda">× base já pareada · ①②③ separadores renumerados · ⊢ ⊣ marcadores fixos da fita</div>'
    )
    with st.expander("Rastreamento completo do ALL"):
        st.dataframe(
            [
                {"passo": numero, "estado": item.estado, "cabeçote": item.posicao_cabecote,
                 "fita": "".join(item.fita), "ação": item.acao}
                for numero, item in enumerate(passos)
            ],
            hide_index=True,
            width="stretch",
        )


def mostrar_derivacao(resultado: ResultadoDuasEtapas) -> None:
    st.subheader("Derivação mais à esquerda na GLC G1")
    if not resultado.derivacao:
        st.info("Sem derivação: a cadeia não pertence a L1, então não há derivação a partir de S.")
        return
    linhas = [resultado.derivacao[0]] + [f"⇒ {forma}" for forma in resultado.derivacao[1:]]
    st.caption(f"{len(resultado.derivacao) - 1} aplicações de produções, sempre na variável mais à esquerda.")
    st.code("\n".join(linhas), language=None)


def mostrar_decisao(resultado: ResultadoDuasEtapas) -> None:
    titulo = f"**{DESCRICAO_DA_DECISAO[resultado.decisao]}**"
    if resultado.decisao == ACEITA:
        st.success(f"{titulo}  \n{resultado.mensagem}")
    elif resultado.decisao == ERRO_DE_ALFABETO:
        st.warning(f"{titulo}  \n{resultado.mensagem}")
    else:
        st.error(f"{titulo}  \n{resultado.mensagem}")


def definir_entrada(cadeia: str) -> None:
    st.session_state["entrada"] = cadeia


def mostrar_botoes_de_exemplo() -> None:
    exemplos = {ROTULO_DO_CENARIO[cenario["esperado"]]: cenario["entrada"]
                for cenario in carregar_registros("cenarios_integracao.json")}
    exemplos.update(EXEMPLOS_ADICIONAIS)
    colunas = st.columns(len(exemplos))
    for coluna, (rotulo, cadeia) in zip(colunas, exemplos.items()):
        coluna.button(rotulo, on_click=definir_entrada, args=(cadeia,), help=cadeia, width="stretch")


def pagina_do_validador() -> None:
    st.session_state.setdefault("entrada", CADEIA_DE_REFERENCIA)
    mostrar_botoes_de_exemplo()
    entrada = st.text_input(
        "Cadeia de entrada",
        key="entrada",
        help="Haste em maiúsculas, laço em minúsculas, '#' e quatro blocos separados por '.'",
    )
    st.caption(f"{len(entrada)} caracteres · Σ = {{{', '.join(sorted(ALFABETO_ENTRADA))}}}")
    if not entrada:
        st.info("Digite uma cadeia ou escolha um exemplo.")
        return

    resultado = validar_em_duas_etapas(entrada)
    mostrar_decisao(resultado)
    if resultado.decisao == ERRO_DE_ALFABETO:
        desenhar_html(entrada_com_simbolo_invalido(entrada, resultado.erro_de_alfabeto.posicao))
        st.caption("Nenhum autômato foi executado: a entrada é conferida contra o alfabeto antes da etapa 1.")
        return

    aba_ap, aba_all, aba_derivacao = st.tabs(["Etapa 1 · AP", "Etapa 2 · ALL", "Derivação GLC"])
    with aba_ap:
        mostrar_etapa_do_ap(resultado)
    with aba_all:
        mostrar_etapa_do_all(resultado)
    with aba_derivacao:
        mostrar_derivacao(resultado)


def pagina_dos_automatos() -> None:
    st.subheader("GLC G1")
    st.code("\n".join(f"{variavel} -> {' | '.join(lados)}" for variavel, lados in PRODUCOES.items()), language=None)

    st.subheader(f"AP · {len(ESTADOS_DO_AP)} estados, aceitação por estado final q16")
    st.caption(f"Configuração inicial: q0, posição 0, pilha [{FUNDO_DA_PILHA}]. Combinação ausente da tabela: rejeita.")
    st.dataframe(
        [
            {"estado": estado, "lê": simbolo, "topo": descrever_topo(topo), "vai para": novo_estado, "pilha": operacao}
            for (estado, simbolo, topo), (novo_estado, operacao) in TRANSICOES_DO_AP.items()
        ],
        hide_index=True,
        width="stretch",
    )

    st.subheader(f"ALL · {len(ESTADOS_DO_ALL)} estados, fita ⊢ c1 … cn ⊣")
    st.caption("Configuração inicial: estado inicio, cabeçote em ⊢. Combinação ausente da tabela: rejeita.")
    st.dataframe(
        [
            {"estado": estado, "lê": lido, "vai para": novo_estado, "escreve": escrito,
             "movimento": DESCRICAO_DO_MOVIMENTO[movimento]}
            for (estado, lido), (novo_estado, escrito, movimento) in TRANSICOES_DO_ALL.items()
        ],
        hide_index=True,
        width="stretch",
    )


def pagina_dos_casos_de_teste() -> None:
    st.caption("Cada cadeia de dados/ é executada agora pelos autômatos e comparada com a decisão registrada.")
    for modulo in ARQUIVOS_DE_DADOS:
        linhas = conferir_registros(modulo)
        aprovados = sum(linha.aprovado for linha in linhas)
        st.subheader(f"{modulo} · {aprovados} de {len(linhas)} aprovados")
        st.dataframe(
            [
                {"entrada": linha.entrada, "tamanho": len(linha.entrada), "esperado": linha.esperado,
                 "obtido": linha.obtido, "regra verificada": linha.regra,
                 "resultado": "✅ aprovado" if linha.aprovado else "❌ reprovado"}
                for linha in linhas
            ],
            hide_index=True,
            width="stretch",
        )


def main() -> None:
    st.set_page_config(page_title="RNA: grampo e pseudonó", page_icon="🧬", layout="wide")
    desenhar_html(ESTILO)
    st.title("Validador de RNA: do grampo ao pseudonó")
    st.caption(
        "Etapa 1: um AP confere o grampo w · laço · w̄ᴿ e o formato # B1.B2.B3.B4. "
        "Etapa 2: um ALL confere o pseudonó x . y . x̄ᴿ . ȳᴿ no trecho após #."
    )
    aba_validador, aba_automatos, aba_casos = st.tabs(["Validador", "Autômatos e GLC", "Casos de teste"])
    with aba_validador:
        pagina_do_validador()
    with aba_automatos:
        pagina_dos_automatos()
    with aba_casos:
        pagina_dos_casos_de_teste()


main()
