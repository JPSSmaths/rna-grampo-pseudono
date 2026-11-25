from dataclasses import dataclass

from rna_validador.alfabeto import SimboloInvalidoErro, validar_entrada
from rna_validador.automato_limitado import executar_automato_limitado
from rna_validador.automato_pilha import executar_automato_pilha
from rna_validador.gramatica import gerar_derivacao
from rna_validador.rastreamento import ResultadoExecucao

SEPARADOR_DE_ETAPAS = "#"

ACEITA = "aceita"
REJEITADA_NO_AP = "rejeitada_no_ap"
REJEITADA_NO_ALL = "rejeitada_no_all"
ERRO_DE_ALFABETO = "erro_de_alfabeto"

DESCRICAO_DA_DECISAO = {
    ACEITA: "Aceita nos dois módulos",
    REJEITADA_NO_AP: "Rejeitada pelo AP (o ALL não é executado)",
    REJEITADA_NO_ALL: "Aceita pelo AP e rejeitada pelo ALL",
    ERRO_DE_ALFABETO: "Erro de entrada: símbolo fora do alfabeto",
}


@dataclass(frozen=True)
class ResultadoDuasEtapas:
    entrada: str
    decisao: str
    mensagem: str
    erro_de_alfabeto: SimboloInvalidoErro | None = None
    resultado_ap: ResultadoExecucao | None = None
    derivacao: tuple[str, ...] = ()
    entrada_all: str | None = None
    resultado_all: ResultadoExecucao | None = None

    @property
    def aceita(self) -> bool:
        return self.decisao == ACEITA


def trecho_apos_o_separador_de_etapas(entrada: str) -> str:
    return entrada[entrada.index(SEPARADOR_DE_ETAPAS) + 1:]


def validar_em_duas_etapas(entrada: str) -> ResultadoDuasEtapas:
    try:
        validar_entrada(entrada)
    except SimboloInvalidoErro as erro:
        return ResultadoDuasEtapas(entrada, ERRO_DE_ALFABETO, str(erro), erro_de_alfabeto=erro)

    resultado_ap = executar_automato_pilha(entrada)
    if not resultado_ap.aceita:
        return ResultadoDuasEtapas(
            entrada, REJEITADA_NO_AP, f"AP rejeitou: {resultado_ap.motivo}", resultado_ap=resultado_ap,
        )

    derivacao = tuple(gerar_derivacao(entrada))
    entrada_all = trecho_apos_o_separador_de_etapas(entrada)
    resultado_all = executar_automato_limitado(entrada_all)
    decisao = ACEITA if resultado_all.aceita else REJEITADA_NO_ALL
    veredito_do_all = "aceitou" if resultado_all.aceita else "rejeitou"
    return ResultadoDuasEtapas(
        entrada,
        decisao,
        f"AP aceitou ({resultado_ap.motivo}); ALL {veredito_do_all}: {resultado_all.motivo}",
        resultado_ap=resultado_ap,
        derivacao=derivacao,
        entrada_all=entrada_all,
        resultado_all=resultado_all,
    )
