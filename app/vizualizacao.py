import html

from rna_validador.rastreamento import PassoAutomatoLimitado, PassoAutomatoPilha


def formatar_pilha(passo: PassoAutomatoPilha) -> str:
    return " | ".join(passo.pilha)


def formatar_fita_em_html(passo: PassoAutomatoLimitado) -> str:
    celulas = []
    for indice, simbolo in enumerate(passo.fita):
        simbolo_seguro = html.escape(simbolo)
        if indice == passo.posicao_cabecote:
            estilo = (
                "display:inline-block;min-width:26px;padding:4px 6px;margin:2px;"
                "border:2px solid #d9534f;border-radius:4px;background-color:#fdecea;"
                "color:#111;font-family:monospace;font-weight:700;text-align:center;"
            )
        else:
            estilo = (
                "display:inline-block;min-width:26px;padding:4px 6px;margin:2px;"
                "border:1px solid #bbb;border-radius:4px;background-color:#f8f9fa;"
                "color:#111;font-family:monospace;text-align:center;"
            )
        celulas.append(f'<span style="{estilo}">{simbolo_seguro}</span>')
    return '<div style="overflow-x:auto;white-space:nowrap;padding:4px 0;">' + "".join(celulas) + "</div>"