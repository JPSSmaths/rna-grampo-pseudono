from dataclasses import dataclass
import json
from pathlib import Path

from rna_validador.alfabeto import SimboloInvalidoErro
from rna_validador.automato_limitado import executar_automato_limitado
from rna_validador.automato_pilha import executar_automato_pilha
from rna_validador.validador_duas_etapas import validar_duas_etapas


@dataclass(frozen=True)
class RegistroTeste:
    modulo: str
    entrada: str
    esperado: str
    obtido: str
    regra: str
    aprovado: bool


def _carregar_json(pasta_dados: Path, nome_arquivo: str) -> list[dict]:
    caminho = pasta_dados / nome_arquivo
    return json.loads(caminho.read_text(encoding="utf-8"))


def _rotulo_booleano(aceita: bool) -> str:
    return "aceita" if aceita else "rejeita"


def _rotulo_integracao(ap_aceita: bool, all_aceita: bool | None) -> str:
    if not ap_aceita:
        return "AP rejeita; ALL não executa"
    if all_aceita:
        return "AP aceita; ALL aceita"
    return "AP aceita; ALL rejeita"


def executar_registros_do_projeto(pasta_dados: Path) -> list[RegistroTeste]:
    registros: list[RegistroTeste] = []

    for item in _carregar_json(pasta_dados, "cadeias_ap.json"):
        esperado = _rotulo_booleano(item["esperado"])
        obtido = _rotulo_booleano(executar_automato_pilha(item["entrada"]).aceita)
        registros.append(
            RegistroTeste(
                modulo="AP",
                entrada=item["entrada"],
                esperado=esperado,
                obtido=obtido,
                regra=item["regra"],
                aprovado=obtido == esperado,
            )
        )

    for item in _carregar_json(pasta_dados, "cadeias_all.json"):
        esperado = _rotulo_booleano(item["esperado"])
        obtido = _rotulo_booleano(executar_automato_limitado(item["entrada"]).aceita)
        registros.append(
            RegistroTeste(
                modulo="ALL",
                entrada=item["entrada"],
                esperado=esperado,
                obtido=obtido,
                regra=item["regra"],
                aprovado=obtido == esperado,
            )
        )

    for item in _carregar_json(pasta_dados, "cenarios_integracao.json"):
        esperado = _rotulo_integracao(item["esperado_ap"], item["esperado_all"])
        resultado = validar_duas_etapas(item["entrada"])
        all_aceita = None if resultado.resultado_all is None else resultado.resultado_all.aceita
        obtido = _rotulo_integracao(resultado.resultado_ap.aceita, all_aceita)
        registros.append(
            RegistroTeste(
                modulo="Integração",
                entrada=item["entrada"],
                esperado=esperado,
                obtido=obtido,
                regra=item["regra"],
                aprovado=obtido == esperado,
            )
        )

    for item in _carregar_json(pasta_dados, "cadeias_invalidas.json"):
        esperado = f"erro: {item['mensagem_esperada']}"
        try:
            resultado = validar_duas_etapas(item["entrada"])
            all_aceita = None if resultado.resultado_all is None else resultado.resultado_all.aceita
            obtido = _rotulo_integracao(resultado.resultado_ap.aceita, all_aceita)
        except SimboloInvalidoErro as erro:
            obtido = f"erro: {erro}"
        registros.append(
            RegistroTeste(
                modulo="Alfabeto",
                entrada=item["entrada"],
                esperado=esperado,
                obtido=obtido,
                regra=item["regra"],
                aprovado=obtido == esperado,
            )
        )

    return registros


def formatar_registros_em_markdown(registros: list[RegistroTeste]) -> str:
    linhas = [
        "| Módulo | Entrada | Esperado | Obtido | Regra | Resultado |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for registro in registros:
        resultado = "aprovado" if registro.aprovado else "reprovado"
        linhas.append(
            f"| {registro.modulo} | `{registro.entrada}` | {registro.esperado} | {registro.obtido} | {registro.regra} | {resultado} |"
        )
    return "\n".join(linhas) + "\n"


def main() -> None:
    raiz = Path(__file__).resolve().parents[2]
    pasta_dados = raiz / "dados"
    registros = executar_registros_do_projeto(pasta_dados)
    conteudo = formatar_registros_em_markdown(registros)
    (pasta_dados / "registro_testes.md").write_text(conteudo, encoding="utf-8")
    aprovados = sum(registro.aprovado for registro in registros)
    print(f"{aprovados} de {len(registros)} aprovados")


if __name__ == "__main__":
    main()  