import json
from pathlib import Path

PASTA_DADOS = Path(__file__).parent.parent / "dados"


def carregar_registros(nome_arquivo: str) -> list[dict]:
    return json.loads((PASTA_DADOS / nome_arquivo).read_text(encoding="utf-8"))
