from pathlib import Path

from streamlit.testing.v1 import AppTest

CAMINHO_DO_APP = str(Path(__file__).parent.parent / "app" / "streamlit_app.py")
TEMPO_LIMITE_EM_SEGUNDOS = 60

CADEIA_DE_REFERENCIA = "GCAUCaaaaGAUGC#AC.GG.GU.CC"
CADEIA_COM_FECHO_ERRADO = "GCAUCaaaaGAUGA#AC.GG.GU.CC"
CADEIA_REJEITADA_PELO_ALL = "GCAUCaaaaGAUGC#AC.GG.GU.GG"
CADEIA_COM_SIMBOLO_FORA_DO_ALFABETO = "GCAUCaaaaGAUGC#AC.GG.GX.CC"


def abrir_app():
    return AppTest.from_file(CAMINHO_DO_APP, default_timeout=TEMPO_LIMITE_EM_SEGUNDOS).run()


def validar(entrada):
    app = abrir_app()
    app.text_input(key="entrada").set_value(entrada)
    return app.run()


def test_o_app_abre_sem_erro_com_a_cadeia_de_referencia():
    app = abrir_app()
    assert not app.exception
    assert app.text_input(key="entrada").value == CADEIA_DE_REFERENCIA


def test_cadeia_de_referencia_e_aceita_pelos_dois_automatos():
    app = validar(CADEIA_DE_REFERENCIA)
    assert not app.exception
    assert app.success[0].value.startswith("**Aceita nos dois módulos**")


def test_cadeia_com_fecho_errado_e_rejeitada_pelo_ap():
    app = validar(CADEIA_COM_FECHO_ERRADO)
    assert not app.exception
    assert app.error[0].value.startswith("**Rejeitada pelo AP (o ALL não é executado)**")
    assert "transição indefinida em q8 ao ler 'A'" in app.error[0].value


def test_cadeia_aceita_pelo_ap_e_rejeitada_pelo_all():
    app = validar(CADEIA_REJEITADA_PELO_ALL)
    assert not app.exception
    assert app.error[0].value.startswith("**Aceita pelo AP e rejeitada pelo ALL**")


def test_simbolo_fora_do_alfabeto_mostra_a_mensagem_sem_executar_automatos():
    app = validar(CADEIA_COM_SIMBOLO_FORA_DO_ALFABETO)
    assert not app.exception
    assert "Símbolo 'X' na posição 23 não pertence ao alfabeto" in app.warning[0].value
    assert not app.success and not app.error


def test_espacos_nas_pontas_sao_ignorados():
    app = validar(f"  {CADEIA_DE_REFERENCIA}  ")
    assert not app.exception
    assert app.success[0].value.startswith("**Aceita nos dois módulos**")


def test_espaco_no_meio_e_simbolo_invalido():
    app = validar("GCAUCaaaaGAUGC #AC.GG.GU.CC")
    assert not app.exception
    assert "Símbolo ' ' na posição 15" in app.warning[0].value


def test_entrada_vazia_pede_uma_cadeia_sem_quebrar():
    app = validar("")
    assert not app.exception
    assert app.info[0].value == "Digite uma cadeia ou escolha um exemplo."


def test_haste_de_500_bases_e_validada_sem_quebrar_a_interface():
    haste = "ACGU" * 125
    app = validar(haste + "aaaa" + haste + "#A.C.U.G")
    assert not app.exception
    assert app.success[0].value.startswith("**Aceita nos dois módulos**")


def test_botao_de_cenario_preenche_a_cadeia_e_valida():
    app = abrir_app()
    botao = next(botao for botao in app.button if botao.label == "Cenário 3 · rejeitada no ALL")
    botao.click()
    app.run()
    assert not app.exception
    assert app.text_input(key="entrada").value == CADEIA_REJEITADA_PELO_ALL
    assert app.error[0].value.startswith("**Aceita pelo AP e rejeitada pelo ALL**")


def test_aba_de_casos_de_teste_mostra_todos_os_modulos_aprovados():
    app = abrir_app()
    assert not app.exception
    titulos = [subtitulo.value for subtitulo in app.subheader]
    assert "AP · 18 de 18 aprovados" in titulos
    assert "ALL · 19 de 19 aprovados" in titulos
    assert "Integração · 3 de 3 aprovados" in titulos
    assert "Alfabeto · 2 de 2 aprovados" in titulos
