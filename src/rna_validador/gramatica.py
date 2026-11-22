import re

from rna_validador.alfabeto import BASES, COMPLEMENTO, LETRAS_LACO
from rna_validador.automato_pilha import executar_automato_pilha

VARIAVEIS = frozenset("SHIKJLMXBN")
VARIAVEIS_DOS_PARES_DA_HASTE = ("H", "I", "K")
VARIAVEL_DOS_PARES_ADICIONAIS = "J"
VARIAVEL_DO_PROXIMO_NIVEL = {"H": "I", "I": "K", "K": "J", "J": "J"}


def lados_direitos_dos_pares(proxima_variavel: str) -> tuple[str, ...]:
    return tuple(f"{base}{proxima_variavel}{COMPLEMENTO[base]}" for base in BASES)


PRODUCOES: dict[str, tuple[str, ...]] = {
    "S": ("H#B.B.B.B",),
    "H": lados_direitos_dos_pares("I"),
    "I": lados_direitos_dos_pares("K"),
    "K": lados_direitos_dos_pares("J"),
    "J": lados_direitos_dos_pares("J") + ("L",),
    "L": ("XXXX", "XXXXM"),
    "M": ("X", "XM"),
    "X": tuple(LETRAS_LACO),
    "B": ("N", "NB"),
    "N": tuple(BASES),
}

PADRAO_HASTE_LACO_FECHO = re.compile(r"([ACGU]+)([acgu]+)([ACGU]+)")


class CadeiaForaDaLinguagemErro(ValueError):
    pass


def variavel_do_par(indice_do_par: int) -> str:
    if indice_do_par < len(VARIAVEIS_DOS_PARES_DA_HASTE):
        return VARIAVEIS_DOS_PARES_DA_HASTE[indice_do_par]
    return VARIAVEL_DOS_PARES_ADICIONAIS


def substituir_variavel_mais_a_esquerda(forma_sentencial: str, lado_direito: str) -> str:
    posicao = next(indice for indice, simbolo in enumerate(forma_sentencial) if simbolo in VARIAVEIS)
    return forma_sentencial[:posicao] + lado_direito + forma_sentencial[posicao + 1:]


def escolhas_do_bloco(bloco: str) -> list[str]:
    escolhas = []
    for posicao, base in enumerate(bloco):
        eh_ultima_base = posicao == len(bloco) - 1
        escolhas.append("N" if eh_ultima_base else "NB")
        escolhas.append(base)
    return escolhas


def escolhas_do_laco(laco: str) -> list[str]:
    quantidade_de_letras_depois_das_quatro_primeiras = len(laco) - 4
    escolhas = ["XXXX" if quantidade_de_letras_depois_das_quatro_primeiras == 0 else "XXXXM"]
    escolhas.extend(laco[:4])
    letras_restantes = laco[4:]
    for posicao, letra in enumerate(letras_restantes):
        eh_ultima_letra = posicao == len(letras_restantes) - 1
        escolhas.append("X" if eh_ultima_letra else "XM")
        escolhas.append(letra)
    return escolhas


def escolhas_da_haste(haste: str) -> list[str]:
    escolhas = []
    for indice_do_par, base in enumerate(haste):
        proxima_variavel = VARIAVEL_DO_PROXIMO_NIVEL[variavel_do_par(indice_do_par)]
        escolhas.append(f"{base}{proxima_variavel}{COMPLEMENTO[base]}")
    return escolhas


def gerar_derivacao(entrada: str) -> list[str]:
    resultado_do_automato = executar_automato_pilha(entrada)
    if not resultado_do_automato.aceita:
        raise CadeiaForaDaLinguagemErro(resultado_do_automato.motivo)

    parte_do_grampo, parte_dos_blocos = entrada.split("#", 1)
    haste, laco, _ = PADRAO_HASTE_LACO_FECHO.fullmatch(parte_do_grampo).groups()

    escolhas = ["H#B.B.B.B"]
    escolhas.extend(escolhas_da_haste(haste))
    escolhas.append("L")
    escolhas.extend(escolhas_do_laco(laco))
    for bloco in parte_dos_blocos.split("."):
        escolhas.extend(escolhas_do_bloco(bloco))

    derivacao = ["S"]
    for lado_direito in escolhas:
        derivacao.append(substituir_variavel_mais_a_esquerda(derivacao[-1], lado_direito))
    return derivacao
