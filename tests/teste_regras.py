from pathlib import Path
import pytest
from rna_validador.registro_testes import executar_registros_do_projeto, formatar_registros_em_markdown
from tests.dados_de_teste import carregar_registros

PASTA_DADOS = Path(__file__).parent.parent / "dados"
ARQUIVOS = ["cadeias_ap.json", "cadeias_all.json", "cenarios_integracao.json", "cadeias_invalidas.json"]


@pytest.mark.parametrize("arquivo", ARQUIVOS)
def test_toda_cadeia_tem_18_ou_mais_caracteres(arquivo):
    assert all(len(registro["entrada"]) >= 18 for registro in carregar_registros(arquivo))


@pytest.mark.parametrize("arquivo", ["cadeias_ap.json", "cadeias_all.json"])
def test_cada_modulo_tem_8_aceitas_e_8_rejeitadas_distintas(arquivo):
    registros = carregar_registros(arquivo)
    entradas = [registro["entrada"] for registro in registros]
    assert len(set(entradas)) == len(entradas)
    assert sum(r["esperado"] for r in registros) >= 8
    assert sum(not r["esperado"] for r in registros) >= 8


def test_todos_os_registros_do_projeto_sao_aprovados():
    registros = executar_registros_do_projeto(PASTA_DADOS)
    assert len(registros) == 18 + 19 + 3 + 2
    assert all(registro.aprovado for registro in registros)


def test_markdown_traz_cabecalho_e_uma_linha_por_registro():
    registros = executar_registros_do_projeto(PASTA_DADOS)
    linhas = formatar_registros_em_markdown(registros).splitlines()
    assert linhas[0] == "| Módulo | Entrada | Esperado | Obtido | Regra | Resultado |"
    assert len(linhas) == len(registros) + 2