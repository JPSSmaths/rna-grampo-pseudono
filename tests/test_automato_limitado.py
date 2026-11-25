import random
import pytest
from rna_validador.alfabeto import ALFABETO_ALL, SimboloInvalidoErro, complemento_reverso
from rna_validador.automato_limitado import ESTADOS, executar_automato_limitado
from tests.dados_de_teste import carregar_registros

REGISTROS = carregar_registros("cadeias_all.json")


def oraculo_l2(entrada):
    blocos = entrada.split(".")
    return (len(blocos) == 4 and all(blocos)
            and blocos[2] == complemento_reverso(blocos[0])
            and blocos[3] == complemento_reverso(blocos[1]))


def respeita_a_fita(resultado, quantidade_de_celulas):
    return all(
        len(passo.fita) == quantidade_de_celulas + 2 and passo.fita[0] == "⊢" and passo.fita[-1] == "⊣"
        and 0 <= passo.posicao_cabecote <= quantidade_de_celulas + 1
        for passo in resultado.passos
    )


@pytest.mark.parametrize("registro", REGISTROS, ids=lambda registro: registro["regra"])
def test_decisao_do_all_confere_com_o_esperado(registro):
    resultado = executar_automato_limitado(registro["entrada"])
    assert resultado.aceita == registro["esperado"]
    assert respeita_a_fita(resultado, len(registro["entrada"]))


def test_all_tem_pelo_menos_8_estados():
    assert len(ESTADOS) >= 8 and {"inicio", "aceita", "rejeita"} <= set(ESTADOS)


def test_rastreamento_da_menor_entrada_aceita():
    resultado = executar_automato_limitado("ACGUA.GCA.UACGU.UGC")
    primeiro, ultimo = resultado.passos[0], resultado.passos[-1]
    assert (primeiro.estado, primeiro.posicao_cabecote) == ("inicio", 0)
    assert primeiro.fita == ("⊢", *"ACGUA.GCA.UACGU.UGC", "⊣")
    assert ultimo.estado == "aceita"
    assert ultimo.fita == ("⊢", "×", "×", "×", "×", "×", "①", "×", "×", "×", "②", "×", "×", "×", "×", "×", "③", "×", "×", "×", "⊣")


def test_entrada_vazia_e_rejeitada_sem_erro():
    assert not executar_automato_limitado("").aceita


def test_simbolo_do_ap_na_entrada_do_all_levanta_erro():
    with pytest.raises(SimboloInvalidoErro):
        executar_automato_limitado("ACGUA.GCA#UACGU.UGC")


def test_entrada_de_243_celulas_termina_dentro_do_limite_quadratico():
    x, y = "ACGU" * 20, "GGCA" * 10
    entrada = f"{x}.{y}.{complemento_reverso(x)}.{complemento_reverso(y)}"
    resultado = executar_automato_limitado(entrada)
    assert len(entrada) == 243 and resultado.aceita
    assert len(resultado.passos) <= 4 * (len(entrada) + 2) ** 2


def test_cadeias_aleatorias_nunca_saem_da_fita_nem_levantam_excecao():
    sorteio = random.Random(3)
    simbolos = sorted(ALFABETO_ALL)
    for _ in range(300):
        entrada = "".join(sorteio.choice(simbolos) for _ in range(sorteio.randrange(0, 26)))
        resultado = executar_automato_limitado(entrada)
        assert respeita_a_fita(resultado, len(entrada)) and resultado.aceita == oraculo_l2(entrada), entrada


def test_equivale_ao_oraculo_em_mutacoes_das_cadeias_do_projeto():
    sorteio = random.Random(11)
    simbolos = sorted(ALFABETO_ALL)
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
            assert executar_automato_limitado(mutada).aceita == oraculo_l2(mutada), mutada
