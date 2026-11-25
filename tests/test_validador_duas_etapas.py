import json
from pathlib import Path

import pytest
from rna_validador.conferencia import ARQUIVOS_DE_DADOS, conferir_registros
from rna_validador.validador_duas_etapas import (
    ACEITA, ERRO_DE_ALFABETO, REJEITADA_NO_ALL, REJEITADA_NO_AP, validar_em_duas_etapas,
)
from tests.dados_de_teste import PASTA_DADOS, carregar_registros

CENARIOS = carregar_registros("cenarios_integracao.json")


@pytest.mark.parametrize("cenario", CENARIOS, ids=lambda cenario: cenario["esperado"])
def test_cenario_de_integracao_confere_com_o_esperado(cenario):
    assert validar_em_duas_etapas(cenario["entrada"]).decisao == cenario["esperado"]


def test_os_tres_cenarios_obrigatorios_estao_registrados():
    assert sorted(cenario["esperado"] for cenario in CENARIOS) == sorted([ACEITA, REJEITADA_NO_AP, REJEITADA_NO_ALL])


def test_cadeia_aceita_passa_o_trecho_apos_cerquilha_ao_all():
    resultado = validar_em_duas_etapas("GCAUCaaaaGAUGC#AC.GG.GU.CC")
    assert resultado.aceita and resultado.decisao == ACEITA
    assert resultado.resultado_ap.aceita and resultado.resultado_all.aceita
    assert resultado.entrada_all == "AC.GG.GU.CC"
    assert resultado.resultado_all.passos[0].fita == ("⊢", *"AC.GG.GU.CC", "⊣")


def test_cadeia_aceita_pelo_ap_traz_a_derivacao_da_glc():
    resultado = validar_em_duas_etapas("GCAUCaaaaGAUGC#AC.GG.GU.GG")
    assert resultado.derivacao[0] == "S" and resultado.derivacao[-1] == "GCAUCaaaaGAUGC#AC.GG.GU.GG"


def test_rejeicao_no_ap_nao_executa_o_all():
    resultado = validar_em_duas_etapas("GCAUCaaaaGAUGA#AC.GG.GU.CC")
    assert not resultado.aceita and resultado.decisao == REJEITADA_NO_AP
    assert not resultado.resultado_ap.aceita
    assert resultado.resultado_all is None and resultado.entrada_all is None
    assert resultado.derivacao == ()
    assert resultado.resultado_ap.motivo in resultado.mensagem


def test_rejeicao_no_all_informa_o_motivo_do_all():
    resultado = validar_em_duas_etapas("GCAUCaaaaGAUGC#AC.GG.GU.GG")
    assert not resultado.aceita and resultado.decisao == REJEITADA_NO_ALL
    assert resultado.resultado_ap.aceita and not resultado.resultado_all.aceita
    assert resultado.resultado_all.motivo in resultado.mensagem


def test_simbolo_fora_do_alfabeto_gera_mensagem_antes_de_qualquer_automato():
    resultado = validar_em_duas_etapas("GCAUCaaaaGAUGC#AC.GG.GT.CC")
    assert not resultado.aceita and resultado.decisao == ERRO_DE_ALFABETO
    assert resultado.mensagem == "Símbolo 'T' na posição 23 não pertence ao alfabeto {#, ., A, C, G, U, a, c, g, u}"
    assert (resultado.erro_de_alfabeto.simbolo, resultado.erro_de_alfabeto.posicao) == ("T", 23)
    assert resultado.resultado_ap is None and resultado.resultado_all is None


def test_entrada_vazia_e_rejeitada_no_ap_sem_erro():
    resultado = validar_em_duas_etapas("")
    assert resultado.decisao == REJEITADA_NO_AP and resultado.resultado_all is None


@pytest.mark.parametrize("modulo", list(ARQUIVOS_DE_DADOS))
def test_conferencia_dos_dados_aprova_todos_os_registros(modulo):
    linhas = conferir_registros(modulo)
    assert linhas and all(linha.aprovado for linha in linhas)
    assert all(linha.obtido == linha.esperado for linha in linhas)


def test_conferencia_registra_entrada_decisoes_e_regra():
    primeira = conferir_registros("Integração")[0]
    assert (primeira.entrada, primeira.esperado, primeira.obtido) == ("GCAUCaaaaGAUGC#AC.GG.GU.CC", ACEITA, ACEITA)
    assert primeira.regra.startswith("Cenário 1")


@pytest.mark.parametrize("arquivo", sorted(Path(PASTA_DADOS).glob("*.json")), ids=lambda arquivo: arquivo.name)
def test_nenhuma_cadeia_dos_dados_tem_menos_de_18_caracteres(arquivo):
    registros = json.loads(arquivo.read_text(encoding="utf-8"))
    assert all(len(registro["entrada"]) >= 18 for registro in registros)


def test_conferencia_inclui_o_modulo_de_alfabeto_com_a_mensagem_de_erro():
    linhas = conferir_registros("Alfabeto")
    assert len(linhas) == 2
    assert all(linha.aprovado for linha in linhas)
    assert linhas[0].obtido == "erro: Símbolo 'X' na posição 23 não pertence ao alfabeto {#, ., A, C, G, U, a, c, g, u}"
