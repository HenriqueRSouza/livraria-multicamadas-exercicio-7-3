"""Reserva (estados) e fidelidade (R05)."""
from dataclasses import dataclass

from .erros import RegraInvalida


@dataclass
class Reserva:
    id: int
    cliente_id: int
    estado: str

    def _validar(self, cliente_id):
        if self.cliente_id != cliente_id or self.estado != "confirmada":
            raise RegraInvalida("Reserva inexistente, de outro cliente ou já finalizada.")

    def cancelar(self, cliente_id):
        self._validar(cliente_id)
        self.estado = "cancelada"

    def retirar(self, cliente_id):
        self._validar(cliente_id)
        self.estado = "retirada"


def pontos(compras):
    """Um ponto por real inteiro de cada compra concluída."""
    return sum(c["preco_centavos"] // 100 for c in compras)
