from dataclasses import dataclass


@dataclass(frozen=True)
class PassoAutomatoPilha:
    estado: str
    posicao: int
    pilha: tuple[str, ...]
    acao: str


@dataclass(frozen=True)
class PassoAutomatoLimitado:
    estado: str
    fita: tuple[str, ...]
    posicao_cabecote: int
    acao: str


@dataclass(frozen=True)
class ResultadoExecucao:
    aceita: bool
    passos: tuple
    motivo: str
