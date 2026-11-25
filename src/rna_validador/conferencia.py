import json
from dataclasses import dataclass
from pathlib import Path

from rna_validador.automato_limitado import executar_automato_limitado
from rna_validador.automato_pilha import executar_automato_pilha
from rna_validador.validador_duas_etapas import ERRO_DE_ALFABETO, validar_em_duas_etapas

PASTA_DADOS = Path(__file__).resolve().parents[2] / "dados"

ACEITA, REJEITADA = "aceita", "rejeitada"
PREFIXO_DE_ERRO = "erro: "
SEM_ERRO_DE_ALFABETO = "sem erro de alfabeto"


def decisao_do_modulo(aceita: bool) -> str:
    return ACEITA if aceita else REJEITADA


def decidir_no_ap(entrada: str) -> str:
    return decisao_do_modulo(executar_automato_pilha(entrada).aceita)


def decidir_no_all(entrada: str) -> str:
    return decisao_do_modulo(executar_automato_limitado(entrada).aceita)


def decidir_nas_duas_etapas(entrada: str) -> str:
    return validar_em_duas_etapas(entrada).decisao


def decidir_no_alfabeto(entrada: str) -> str:
    resultado = validar_em_duas_etapas(entrada)
    if resultado.decisao == ERRO_DE_ALFABETO:
        return PREFIXO_DE_ERRO + resultado.mensagem
    return SEM_ERRO_DE_ALFABETO


def esperado_do_registro(registro: dict) -> str:
    if "mensagem_esperada" in registro:
        return PREFIXO_DE_ERRO + registro["mensagem_esperada"]
    esperado = registro["esperado"]
    return decisao_do_modulo(esperado) if isinstance(esperado, bool) else esperado


ARQUIVOS_DE_DADOS = {
    "AP": ("cadeias_ap.json", decidir_no_ap),
    "ALL": ("cadeias_all.json", decidir_no_all),
    "Integração": ("cenarios_integracao.json", decidir_nas_duas_etapas),
    "Alfabeto": ("cadeias_invalidas.json", decidir_no_alfabeto),
}


@dataclass(frozen=True)
class LinhaConferida:
    entrada: str
    esperado: str
    obtido: str
    regra: str

    @property
    def aprovado(self) -> bool:
        return self.esperado == self.obtido


def carregar_registros(nome_arquivo: str) -> list[dict]:
    return json.loads((PASTA_DADOS / nome_arquivo).read_text(encoding="utf-8"))


def conferir_registros(modulo: str) -> list[LinhaConferida]:
    nome_arquivo, decidir = ARQUIVOS_DE_DADOS[modulo]
    return [
        LinhaConferida(registro["entrada"], esperado_do_registro(registro), decidir(registro["entrada"]), registro["regra"])
        for registro in carregar_registros(nome_arquivo)
    ]
