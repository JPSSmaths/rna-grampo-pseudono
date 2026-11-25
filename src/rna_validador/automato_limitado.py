from rna_validador.alfabeto import ALFABETO_ALL, BASES, COMPLEMENTO, validar_entrada
from rna_validador.rastreamento import PassoAutomatoLimitado, ResultadoExecucao

MARCADOR_ESQUERDO = "⊢"
MARCADOR_DIREITO = "⊣"
SEPARADOR = "."
MARCA_PAREADA = "×"
PRIMEIRO_SEPARADOR, SEGUNDO_SEPARADOR, TERCEIRO_SEPARADOR = "①", "②", "③"
SEPARADORES_RENUMERADOS = (PRIMEIRO_SEPARADOR, SEGUNDO_SEPARADOR, TERCEIRO_SEPARADOR)

SIMBOLOS_FITA = (
    *BASES, SEPARADOR, MARCA_PAREADA, *SEPARADORES_RENUMERADOS, MARCADOR_ESQUERDO, MARCADOR_DIREITO,
)

DIREITA, ESQUERDA, PARADO = "D", "E", "P"
DESLOCAMENTO = {DIREITA: 1, ESQUERDA: -1, PARADO: 0}
DESCRICAO_DO_MOVIMENTO = {DIREITA: "move à direita", ESQUERDA: "move à esquerda", PARADO: "fica parado"}

ESTADO_INICIAL = "inicio"
ESTADO_ACEITA = "aceita"
ESTADO_REJEITA = "rejeita"
ESTADOS_DE_PARADA = frozenset({ESTADO_ACEITA, ESTADO_REJEITA})

BLOCOS = ("B1", "B2", "B3", "B4")
ESTADOS_DA_PREPARACAO = tuple(
    estado for bloco in BLOCOS for estado in (f"preparacao_espera_{bloco}", f"preparacao_{bloco}")
) + ("preparacao_retorno",)

ESTADOS = (
    ESTADO_INICIAL,
    *ESTADOS_DA_PREPARACAO,
    "busca_livre_B1",
    *(f"levar_B1_{base}" for base in BASES),
    *(f"voltar_B3_{base}" for base in BASES),
    "retornar_fase1",
    "verificar_B3_vazio_cruzando_B2",
    "verificar_B3_vazio",
    "busca_livre_B2",
    *(f"levar_B2_{base}" for base in BASES),
    *(f"voltar_B4_{base}" for base in BASES),
    "retornar_fase2",
    "verificar_B4_vazio",
    ESTADO_ACEITA,
    ESTADO_REJEITA,
)


class ViolacaoLimiteFitaErro(RuntimeError):
    pass


def construir_tabela_de_transicoes():
    tabela = {}

    def adicionar(estado, lido, novo_estado, escrito, movimento):
        tabela[(estado, lido)] = (novo_estado, escrito, movimento)

    def atravessar(estado, simbolos, movimento):
        for simbolo in simbolos:
            adicionar(estado, simbolo, estado, simbolo, movimento)

    def rejeitar(estado, simbolos):
        for simbolo in simbolos:
            adicionar(estado, simbolo, ESTADO_REJEITA, simbolo, PARADO)

    adicionar(ESTADO_INICIAL, MARCADOR_ESQUERDO, "preparacao_espera_B1", MARCADOR_ESQUERDO, DIREITA)

    for indice, bloco in enumerate(BLOCOS):
        espera_bloco, dentro_do_bloco = f"preparacao_espera_{bloco}", f"preparacao_{bloco}"
        for base in BASES:
            adicionar(espera_bloco, base, dentro_do_bloco, base, DIREITA)
        atravessar(dentro_do_bloco, BASES, DIREITA)
        rejeitar(espera_bloco, (SEPARADOR, MARCADOR_DIREITO))
        if bloco == BLOCOS[-1]:
            rejeitar(dentro_do_bloco, SEPARADOR)
            adicionar(dentro_do_bloco, MARCADOR_DIREITO, "preparacao_retorno", MARCADOR_DIREITO, ESQUERDA)
        else:
            proximo_bloco = f"preparacao_espera_{BLOCOS[indice + 1]}"
            adicionar(dentro_do_bloco, SEPARADOR, proximo_bloco, SEPARADORES_RENUMERADOS[indice], DIREITA)
            rejeitar(dentro_do_bloco, MARCADOR_DIREITO)

    atravessar("preparacao_retorno", (*BASES, *SEPARADORES_RENUMERADOS), ESQUERDA)
    adicionar("preparacao_retorno", MARCADOR_ESQUERDO, "busca_livre_B1", MARCADOR_ESQUERDO, DIREITA)

    atravessar("busca_livre_B1", MARCA_PAREADA, DIREITA)
    adicionar("busca_livre_B1", PRIMEIRO_SEPARADOR, "verificar_B3_vazio_cruzando_B2", PRIMEIRO_SEPARADOR, DIREITA)
    for guardada in BASES:
        levar, voltar = f"levar_B1_{guardada}", f"voltar_B3_{guardada}"
        adicionar("busca_livre_B1", guardada, levar, MARCA_PAREADA, DIREITA)
        atravessar(levar, (*BASES, MARCA_PAREADA, PRIMEIRO_SEPARADOR, SEGUNDO_SEPARADOR), DIREITA)
        adicionar(levar, TERCEIRO_SEPARADOR, voltar, TERCEIRO_SEPARADOR, ESQUERDA)
        atravessar(voltar, MARCA_PAREADA, ESQUERDA)
        adicionar(voltar, COMPLEMENTO[guardada], "retornar_fase1", MARCA_PAREADA, ESQUERDA)
        rejeitar(voltar, (*(base for base in BASES if base != COMPLEMENTO[guardada]), SEGUNDO_SEPARADOR))

    atravessar("retornar_fase1", (*BASES, MARCA_PAREADA, *SEPARADORES_RENUMERADOS), ESQUERDA)
    adicionar("retornar_fase1", MARCADOR_ESQUERDO, "busca_livre_B1", MARCADOR_ESQUERDO, DIREITA)

    atravessar("verificar_B3_vazio_cruzando_B2", BASES, DIREITA)
    adicionar("verificar_B3_vazio_cruzando_B2", SEGUNDO_SEPARADOR, "verificar_B3_vazio", SEGUNDO_SEPARADOR, DIREITA)
    atravessar("verificar_B3_vazio", MARCA_PAREADA, DIREITA)
    rejeitar("verificar_B3_vazio", BASES)
    adicionar("verificar_B3_vazio", TERCEIRO_SEPARADOR, "retornar_fase2", TERCEIRO_SEPARADOR, ESQUERDA)

    atravessar("busca_livre_B2", MARCA_PAREADA, DIREITA)
    adicionar("busca_livre_B2", SEGUNDO_SEPARADOR, "verificar_B4_vazio", SEGUNDO_SEPARADOR, DIREITA)
    for guardada in BASES:
        levar, voltar = f"levar_B2_{guardada}", f"voltar_B4_{guardada}"
        adicionar("busca_livre_B2", guardada, levar, MARCA_PAREADA, DIREITA)
        atravessar(levar, (*BASES, MARCA_PAREADA, SEGUNDO_SEPARADOR, TERCEIRO_SEPARADOR), DIREITA)
        adicionar(levar, MARCADOR_DIREITO, voltar, MARCADOR_DIREITO, ESQUERDA)
        atravessar(voltar, MARCA_PAREADA, ESQUERDA)
        adicionar(voltar, COMPLEMENTO[guardada], "retornar_fase2", MARCA_PAREADA, ESQUERDA)
        rejeitar(voltar, (*(base for base in BASES if base != COMPLEMENTO[guardada]), TERCEIRO_SEPARADOR))

    atravessar("retornar_fase2", (*BASES, MARCA_PAREADA, SEGUNDO_SEPARADOR, TERCEIRO_SEPARADOR), ESQUERDA)
    adicionar("retornar_fase2", PRIMEIRO_SEPARADOR, "busca_livre_B2", PRIMEIRO_SEPARADOR, DIREITA)

    atravessar("verificar_B4_vazio", (MARCA_PAREADA, TERCEIRO_SEPARADOR), DIREITA)
    rejeitar("verificar_B4_vazio", BASES)
    adicionar("verificar_B4_vazio", MARCADOR_DIREITO, ESTADO_ACEITA, MARCADOR_DIREITO, PARADO)
    return tabela


TABELA_TRANSICOES = construir_tabela_de_transicoes()


def executar_automato_limitado(entrada: str) -> ResultadoExecucao:
    validar_entrada(entrada, ALFABETO_ALL)
    fita = [MARCADOR_ESQUERDO, *entrada, MARCADOR_DIREITO]
    ultima_posicao = len(fita) - 1
    estado = ESTADO_INICIAL
    posicao_cabecote = 0
    passos = [PassoAutomatoLimitado(estado, tuple(fita), posicao_cabecote, "configuração inicial")]
    motivo = ""

    while estado not in ESTADOS_DE_PARADA:
        simbolo_lido = fita[posicao_cabecote]
        transicao = TABELA_TRANSICOES.get((estado, simbolo_lido))
        if transicao is None:
            motivo = f"transição indefinida em {estado} ao ler '{simbolo_lido}'"
            return ResultadoExecucao(False, tuple(passos), motivo)
        novo_estado, simbolo_escrito, movimento = transicao
        destino_do_cabecote = posicao_cabecote + DESLOCAMENTO[movimento]
        if not 0 <= destino_do_cabecote <= ultima_posicao:
            raise ViolacaoLimiteFitaErro(
                f"transição de {estado} ao ler '{simbolo_lido}' levaria o cabeçote para a posição "
                f"{destino_do_cabecote}, fora de [0, {ultima_posicao}]"
            )
        fita[posicao_cabecote] = simbolo_escrito
        acao = (
            f"lê '{simbolo_lido}' em {estado}, escreve '{simbolo_escrito}', "
            f"{DESCRICAO_DO_MOVIMENTO[movimento]}, vai para {novo_estado}"
        )
        motivo = f"atingiu o estado {novo_estado} ao ler '{simbolo_lido}' em {estado}"
        estado = novo_estado
        posicao_cabecote = destino_do_cabecote
        passos.append(PassoAutomatoLimitado(estado, tuple(fita), posicao_cabecote, acao))

    return ResultadoExecucao(estado == ESTADO_ACEITA, tuple(passos), motivo)
