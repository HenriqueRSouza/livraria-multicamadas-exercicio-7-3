"""Cliente e regras de cadastro/recomendação (R02, R04)."""
import re
from dataclasses import dataclass

from .erros import RegraInvalida
from .livro import normalizar


@dataclass
class Cliente:
    nome: str
    email: str
    bairro: str
    interesses: str = ""

    def __post_init__(self):
        self.nome, self.email, self.bairro = self.nome.strip(), self.email.strip().lower(), self.bairro.strip()
        self.interesses = ",".join(p.strip() for p in self.interesses.split(",") if p.strip())
        if not self.nome or not self.bairro or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", self.email):
            raise RegraInvalida("Informe nome, email válido e bairro.")

    def interessado_em(self, genero):
        return normalizar(genero) in [normalizar(i) for i in self.interesses.split(",") if i]


def recomendar(cliente, livros, favoritos):
    """Livros do gênero de interesse que ainda não estão nos favoritos."""
    ids_favoritos = {f["id"] for f in favoritos}
    return [b for b in livros if cliente.interessado_em(b["genero"]) and b["id"] not in ids_favoritos]
