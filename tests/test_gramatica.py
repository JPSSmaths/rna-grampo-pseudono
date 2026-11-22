import pytest
from rna_validador.gramatica import PRODUCOES, CadeiaForaDaLinguagemErro, gerar_derivacao
from tests.dados_de_teste import carregar_registros

NAO_TERMINAIS = set("SHIKJLMXBN")


def passo_valido(forma_anterior, forma_seguinte):
    posicao = next(indice for indice, simbolo in enumerate(forma_anterior) if simbolo in NAO_TERMINAIS)
    lado_esquerdo = forma_anterior[posicao]
    prefixo, sufixo = forma_anterior[:posicao], forma_anterior[posicao + 1:]
    return any(forma_seguinte == prefixo + lado_direito + sufixo for lado_direito in PRODUCOES[lado_esquerdo])


def test_derivacao_da_cadeia_de_referencia():
    derivacao = gerar_derivacao("GCAUCaaaaGAUGC#AC.GG.GU.CC")
    assert derivacao[0] == "S" and derivacao[-1] == "GCAUCaaaaGAUGC#AC.GG.GU.CC"
    assert derivacao[1] == "H#B.B.B.B" and derivacao[2] == "GIC#B.B.B.B"
    assert len(derivacao) == 29


@pytest.mark.parametrize(
    "registro",
    [registro for registro in carregar_registros("cadeias_ap.json") if registro["esperado"]],
    ids=lambda registro: registro["entrada"],
)
def test_cada_passo_aplica_uma_producao_na_variavel_mais_a_esquerda(registro):
    derivacao = gerar_derivacao(registro["entrada"])
    assert derivacao[-1] == registro["entrada"]
    assert all(passo_valido(anterior, seguinte) for anterior, seguinte in zip(derivacao, derivacao[1:]))


def test_cadeia_rejeitada_pelo_ap_nao_tem_derivacao():
    with pytest.raises(CadeiaForaDaLinguagemErro):
        gerar_derivacao("GCAUCaaaaGAUGA#AC.GG.GU.CC")
