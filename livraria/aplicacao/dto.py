"""Modelos de leitura montados pela aplicação para a apresentação."""
from dataclasses import dataclass, field
from typing import List

from livraria.dominio.entidades import Avaliacao, Compra, Estoque, Promocao, Reserva


@dataclass
class EdicaoDetalhada:
    id: int
    nome: str
    ano: int
    preco_centavos: int
    preco_final_centavos: int
    promocoes: List[Promocao] = field(default_factory=list)
    estoques: List[Estoque] = field(default_factory=list)


@dataclass
class DetalheLivro:
    id: int
    titulo: str
    autor: str
    genero: str
    sinopse: str
    avaliacoes: List[Avaliacao]
    edicoes: List[EdicaoDetalhada]


@dataclass
class Historico:
    reservas: List[Reserva]
    compras: List[Compra]
    pontos: int
