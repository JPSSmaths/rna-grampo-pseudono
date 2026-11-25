import pytest
from tests.dados_de_teste import carregar_registros


@pytest.mark.parametrize("arquivo", ["cadeias_ap.json", "cadeias_all.json"])
def test_cada_modulo_tem_8_aceitas_e_8_rejeitadas_distintas(arquivo):
    registros = carregar_registros(arquivo)
    entradas = [registro["entrada"] for registro in registros]
    assert len(set(entradas)) == len(entradas)
    assert sum(registro["esperado"] for registro in registros) >= 8
    assert sum(not registro["esperado"] for registro in registros) >= 8


@pytest.mark.parametrize("arquivo", ["cadeias_ap.json", "cadeias_all.json", "cenarios_integracao.json", "cadeias_invalidas.json"])
def test_todo_registro_informa_a_regra_verificada(arquivo):
    assert all(registro["regra"].strip() for registro in carregar_registros(arquivo))
