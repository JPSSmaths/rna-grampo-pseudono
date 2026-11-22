import random
import re
import pytest
from rna_validador.alfabeto import ALFABETO_ENTRADA, SimboloInvalidoErro, complemento_reverso
from rna_validador.automato_pilha import ESTADO_FINAL, ESTADOS, executar_automato_pilha
from rna_validador.rastreamento import PassoAutomatoPilha
from tests.dados_de_teste import carregar_registros

REGISTROS = carregar_registros("cadeias_ap.json")
PADRAO_L1 = re.compile(r"([ACGU]{3,})([acgu]{4,})([ACGU]+)#[ACGU]+\.[ACGU]+\.[ACGU]+\.[ACGU]+")


def oraculo_l1(entrada):
    correspondencia = PADRAO_L1.fullmatch(entrada)
    return bool(correspondencia) and correspondencia.group(3) == complemento_reverso(correspondencia.group(1))


@pytest.mark.parametrize("registro", REGISTROS, ids=lambda registro: registro["regra"])
def test_decisao_do_ap_confere_com_o_esperado(registro):
    assert executar_automato_pilha(registro["entrada"]).aceita == registro["esperado"]


def test_ap_tem_17_estados_e_um_final():
    assert len(ESTADOS) == 17 and ESTADO_FINAL == "q16" and ESTADO_FINAL in ESTADOS


def test_rastreamento_da_cadeia_de_referencia():
    resultado = executar_automato_pilha("GCAUCaaaaGAUGC#AC.GG.GU.CC")
    assert resultado.passos[0] == PassoAutomatoPilha("q0", 0, ("Z0",), "configuração inicial")
    assert len(resultado.passos) == 27
    assert (resultado.passos[5].estado, resultado.passos[5].pilha) == ("q3", ("Z0", "C", "G", "U", "A", "G"))
    assert (resultado.passos[15].estado, resultado.passos[15].pilha) == ("q9", ("Z0",))
    assert (resultado.passos[-1].estado, resultado.passos[-1].posicao, resultado.passos[-1].pilha) == ("q16", 26, ("Z0",))


def test_entrada_vazia_e_rejeitada_sem_erro():
    resultado = executar_automato_pilha("")
    assert not resultado.aceita and len(resultado.passos) == 1 and resultado.motivo


def test_rejeicao_informa_o_motivo():
    assert executar_automato_pilha("GCAUCaaaaGAUGCAC.GG.GU.CC").motivo


def test_simbolo_fora_do_alfabeto_levanta_erro():
    with pytest.raises(SimboloInvalidoErro):
        executar_automato_pilha("GCAUCaaaaGAUGC#AC.GG.GX.CC")


def test_haste_de_500_bases_termina_com_um_passo_por_simbolo():
    haste = "ACGU" * 125
    entrada = haste + "aaaa" + complemento_reverso(haste) + "#A.C.U.G"
    resultado = executar_automato_pilha(entrada)
    assert resultado.aceita and len(resultado.passos) == len(entrada) + 1


def test_equivale_ao_oraculo_em_mutacoes_das_cadeias_do_projeto():
    sorteio = random.Random(7)
    simbolos = sorted(ALFABETO_ENTRADA)
    for registro in REGISTROS:
        for _ in range(60):
            cadeia = list(registro["entrada"])
            posicao = sorteio.randrange(len(cadeia))
            operacao = sorteio.choice(["trocar", "inserir", "apagar"])
            if operacao == "trocar":
                cadeia[posicao] = sorteio.choice(simbolos)
            elif operacao == "inserir":
                cadeia.insert(posicao, sorteio.choice(simbolos))
            else:
                del cadeia[posicao]
            mutada = "".join(cadeia)
            assert executar_automato_pilha(mutada).aceita == oraculo_l1(mutada), mutada
