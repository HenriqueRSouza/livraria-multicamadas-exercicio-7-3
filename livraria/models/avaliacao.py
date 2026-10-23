"""Avaliação de livro por cliente (R07 — nova feature)."""
from dataclasses import dataclass

from .erros import RegraInvalida


@dataclass
class Avaliacao:
    nota: int
    texto: str = ""

    def __post_init__(self):
        try:
            self.nota = int(self.nota)
        except (TypeError, ValueError):
            raise RegraInvalida("A nota deve ser um número de 1 a 5.") from None
        self.texto = (self.texto or "").strip()
        if not 1 <= self.nota <= 5:
            raise RegraInvalida("A nota deve ser um número de 1 a 5.")
        if len(self.texto) > 500:
            raise RegraInvalida("O texto da avaliação aceita até 500 caracteres.")


def media(avaliacoes):
    return round(sum(a["nota"] for a in avaliacoes) / len(avaliacoes), 1) if avaliacoes else None
