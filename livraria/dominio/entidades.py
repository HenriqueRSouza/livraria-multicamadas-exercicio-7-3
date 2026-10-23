"""Entidades da especificação (docs/specs/livraria.md)."""
from dataclasses import dataclass
from typing import Optional

from livraria.dominio.excecoes import RegraInvalida

CONFIRMADA, RETIRADA, CANCELADA = "confirmada", "retirada", "cancelada"


@dataclass
class Livro:
    id: int
    titulo: str
    autor: str
    genero: str
    sinopse: str


@dataclass
class Edicao:
    id: int
    livro_id: int
    nome: str
    ano: int
    preco_centavos: int


@dataclass
class Loja:
    id: int
    nome: str
    bairro: str
    endereco: str
    horario: str
    pagamentos: str
    servicos: str
    cafe: bool
    eventos: str


@dataclass
class Estoque:
    edicao_id: int
    loja_id: int
    quantidade: int
    secao: str
    loja_nome: str = ""


@dataclass
class Promocao:
    id: int
    edicao_id: int
    descricao: str
    desconto_centavos: int
    ativa: bool


@dataclass
class Avaliacao:
    id: int
    livro_id: int
    nota: int
    texto: str
    autor: str


@dataclass
class Cliente:
    id: int
    nome: str
    email: str
    bairro: str
    interesses: str


@dataclass
class Notificacao:
    id: int
    cliente_id: int
    tipo: str
    mensagem: str


@dataclass
class Reserva:
    id: int
    cliente_id: int
    edicao_id: int
    loja_id: int
    codigo: Optional[str]
    estado: str
    preco_centavos: int
    titulo: str = ""
    edicao: str = ""
    loja: str = ""
    secao: str = ""

    def _finalizar(self, estado):
        if self.estado != CONFIRMADA:
            raise RegraInvalida("Reserva inexistente, de outro cliente ou já finalizada.")
        self.estado = estado

    def cancelar(self):
        self._finalizar(CANCELADA)

    def retirar(self):
        self._finalizar(RETIRADA)


@dataclass
class Compra:
    id: int
    cliente_id: int
    edicao_id: int
    loja_id: int
    preco_centavos: int
    reserva_id: Optional[int] = None
    titulo: str = ""
    edicao: str = ""
    loja: str = ""
