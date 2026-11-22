from rna_validador.alfabeto import BASES, COMPLEMENTO, LETRAS_LACO, validar_entrada
from rna_validador.rastreamento import PassoAutomatoPilha, ResultadoExecucao

FUNDO_DA_PILHA = "Z0"
ESTADOS = tuple(f"q{numero}" for numero in range(17))
ESTADO_INICIAL = "q0"
ESTADO_FINAL = "q16"

EMPILHA_COMPLEMENTO = "empilha_complemento"
DESEMPILHA = "desempilha"
PILHA_INALTERADA = "pilha_inalterada"

QUALQUER_TOPO = None


def construir_tabela_de_transicoes():
    tabela = {}

    def adicionar(estado, simbolo, topo, novo_estado, operacao):
        tabela[(estado, simbolo, topo)] = (novo_estado, operacao)

    for base in BASES:
        adicionar("q0", base, QUALQUER_TOPO, "q1", EMPILHA_COMPLEMENTO)
        adicionar("q1", base, QUALQUER_TOPO, "q2", EMPILHA_COMPLEMENTO)
        adicionar("q2", base, QUALQUER_TOPO, "q3", EMPILHA_COMPLEMENTO)
        adicionar("q3", base, QUALQUER_TOPO, "q3", EMPILHA_COMPLEMENTO)
        adicionar("q7", base, base, "q8", DESEMPILHA)
        adicionar("q8", base, base, "q8", DESEMPILHA)
        adicionar("q9", base, QUALQUER_TOPO, "q10", PILHA_INALTERADA)
        adicionar("q10", base, QUALQUER_TOPO, "q10", PILHA_INALTERADA)
        adicionar("q11", base, QUALQUER_TOPO, "q12", PILHA_INALTERADA)
        adicionar("q12", base, QUALQUER_TOPO, "q12", PILHA_INALTERADA)
        adicionar("q13", base, QUALQUER_TOPO, "q14", PILHA_INALTERADA)
        adicionar("q14", base, QUALQUER_TOPO, "q14", PILHA_INALTERADA)
        adicionar("q15", base, QUALQUER_TOPO, "q16", PILHA_INALTERADA)
        adicionar("q16", base, QUALQUER_TOPO, "q16", PILHA_INALTERADA)

    for letra in LETRAS_LACO:
        adicionar("q3", letra, QUALQUER_TOPO, "q4", PILHA_INALTERADA)
        adicionar("q4", letra, QUALQUER_TOPO, "q5", PILHA_INALTERADA)
        adicionar("q5", letra, QUALQUER_TOPO, "q6", PILHA_INALTERADA)
        adicionar("q6", letra, QUALQUER_TOPO, "q7", PILHA_INALTERADA)
        adicionar("q7", letra, QUALQUER_TOPO, "q7", PILHA_INALTERADA)

    adicionar("q8", "#", FUNDO_DA_PILHA, "q9", PILHA_INALTERADA)
    adicionar("q10", ".", QUALQUER_TOPO, "q11", PILHA_INALTERADA)
    adicionar("q12", ".", QUALQUER_TOPO, "q13", PILHA_INALTERADA)
    adicionar("q14", ".", QUALQUER_TOPO, "q15", PILHA_INALTERADA)
    return tabela


TABELA_TRANSICOES = construir_tabela_de_transicoes()


def buscar_transicao(estado, simbolo, topo_da_pilha):
    transicao_com_topo = TABELA_TRANSICOES.get((estado, simbolo, topo_da_pilha))
    if transicao_com_topo is not None:
        return transicao_com_topo
    return TABELA_TRANSICOES.get((estado, simbolo, QUALQUER_TOPO))


def aplicar_operacao_na_pilha(pilha, operacao, simbolo):
    if operacao == EMPILHA_COMPLEMENTO:
        return pilha + (COMPLEMENTO[simbolo],), f"empilha {COMPLEMENTO[simbolo]}"
    if operacao == DESEMPILHA:
        return pilha[:-1], f"desempilha {pilha[-1]}"
    return pilha, "pilha inalterada"


def executar_automato_pilha(entrada: str) -> ResultadoExecucao:
    validar_entrada(entrada)
    estado = ESTADO_INICIAL
    pilha = (FUNDO_DA_PILHA,)
    passos = [PassoAutomatoPilha(estado, 0, pilha, "configuração inicial")]

    for posicao, simbolo in enumerate(entrada):
        transicao = buscar_transicao(estado, simbolo, pilha[-1])
        if transicao is None:
            motivo = f"transição indefinida em {estado} ao ler '{simbolo}'"
            return ResultadoExecucao(False, tuple(passos), motivo)
        estado_anterior = estado
        estado, operacao = transicao
        pilha, descricao_da_operacao = aplicar_operacao_na_pilha(pilha, operacao, simbolo)
        acao = f"lê '{simbolo}' em {estado_anterior}, vai para {estado}, {descricao_da_operacao}"
        passos.append(PassoAutomatoPilha(estado, posicao + 1, pilha, acao))

    if estado != ESTADO_FINAL:
        motivo = f"entrada consumida em {estado}, que não é final"
        return ResultadoExecucao(False, tuple(passos), motivo)
    return ResultadoExecucao(True, tuple(passos), f"entrada consumida em {estado}, estado final")
