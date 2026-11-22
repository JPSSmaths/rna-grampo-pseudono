BASES = "ACGU"
LETRAS_LACO = "acgu"
SEPARADORES_DE_ETAPA = "#."

ALFABETO_ENTRADA = frozenset(BASES + LETRAS_LACO + SEPARADORES_DE_ETAPA)
ALFABETO_ALL = frozenset(BASES + ".")

COMPLEMENTO = {"A": "U", "U": "A", "C": "G", "G": "C"}


class SimboloInvalidoErro(ValueError):
    def __init__(self, simbolo: str, posicao: int, alfabeto: frozenset[str]):
        self.simbolo = simbolo
        self.posicao = posicao
        simbolos_ordenados = ", ".join(sorted(alfabeto))
        super().__init__(
            f"Símbolo '{simbolo}' na posição {posicao} não pertence ao alfabeto {{{simbolos_ordenados}}}"
        )


def validar_entrada(entrada: str, alfabeto: frozenset[str] = ALFABETO_ENTRADA) -> None:
    for indice, simbolo in enumerate(entrada):
        if simbolo not in alfabeto:
            raise SimboloInvalidoErro(simbolo, indice + 1, alfabeto)


def complemento_reverso(sequencia: str) -> str:
    return "".join(COMPLEMENTO[base] for base in reversed(sequencia))
