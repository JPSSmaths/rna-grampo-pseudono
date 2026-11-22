import pytest
from rna_validador.alfabeto import (
    ALFABETO_ALL, ALFABETO_ENTRADA, SimboloInvalidoErro, complemento_reverso, validar_entrada,
)


def test_alfabeto_de_entrada_tem_dez_simbolos():
    assert ALFABETO_ENTRADA == frozenset("ACGUacgu#.")


def test_complemento_reverso_da_haste_de_referencia():
    assert complemento_reverso("GCAUC") == "GAUGC"
    assert complemento_reverso("ACGUA") == "UACGU"


def test_entrada_vazia_e_valida():
    assert validar_entrada("") is None


def test_simbolo_fora_do_alfabeto_informa_simbolo_e_posicao():
    with pytest.raises(SimboloInvalidoErro) as erro:
        validar_entrada("GCAUCaaaaGAUGC#AC.GG.GX.CC")
    assert str(erro.value) == "Símbolo 'X' na posição 23 não pertence ao alfabeto {#, ., A, C, G, U, a, c, g, u}"
    assert (erro.value.simbolo, erro.value.posicao) == ("X", 23)


def test_espaco_no_meio_e_simbolo_invalido():
    with pytest.raises(SimboloInvalidoErro) as erro:
        validar_entrada("GCAUCaaaaGAUGC #AC.GG.GU.CC")
    assert (erro.value.simbolo, erro.value.posicao) == (" ", 15)


def test_letra_cirilica_parecida_com_base_e_rejeitada():
    with pytest.raises(SimboloInvalidoErro) as erro:
        validar_entrada("ACGА")
    assert (erro.value.simbolo, erro.value.posicao) == ("А", 4)


def test_alfabeto_do_all_rejeita_cerquilha():
    with pytest.raises(SimboloInvalidoErro) as erro:
        validar_entrada("ACGUA.GCA#UACGU.UGC", ALFABETO_ALL)
    assert str(erro.value) == "Símbolo '#' na posição 10 não pertence ao alfabeto {., A, C, G, U}"
