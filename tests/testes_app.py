from pathlib import Path
from streamlit.testing.v1 import AppTest

CAMINHO_APP = str(Path(__file__).parent.parent / "app" / "streamlit_app.py")


def validar(entrada):
    app = AppTest.from_file(CAMINHO_APP, default_timeout=30).run()
    app.text_input(key="entrada").set_value(entrada)
    app.button[[botao.label for botao in app.button].index("Validar")].click()
    return app.run()


def test_cadeia_de_referencia_e_aceita_pelos_dois_automatos():
    app = validar("GCAUCaaaaGAUGC#AC.GG.GU.CC")
    assert not app.exception
    assert app.success[0].value == "Aceita pelo AP e pelo ALL"


def test_cadeia_rejeitada_pelo_ap():
    app = validar("GCAUCaaaaGAUGA#AC.GG.GU.CC")
    assert not app.exception
    assert app.error[0].value == "Rejeitada pelo AP"


def test_cadeia_aceita_pelo_ap_e_rejeitada_pelo_all():
    app = validar("GCAUCaaaaGAUGC#AC.GG.GU.GG")
    assert not app.exception
    assert app.error[0].value == "Aceita pelo AP e rejeitada pelo ALL"


def test_simbolo_fora_do_alfabeto_mostra_a_mensagem():
    app = validar("GCAUCaaaaGAUGC#AC.GG.GX.CC")
    assert not app.exception
    assert "Símbolo 'X' na posição 23" in app.error[0].value


def test_espacos_nas_pontas_sao_ignorados():
    app = validar("  GCAUCaaaaGAUGC#AC.GG.GU.CC  ")
    assert not app.exception
    assert app.success[0].value == "Aceita pelo AP e pelo ALL"


def test_entrada_vazia_nao_quebra_a_interface():
    app = validar("")
    assert not app.exception
    assert app.error[0].value == "Rejeitada pelo AP"