"""Camada de aplicação: serviços (casos de uso) e fronteiras de transação.

É a única camada que a apresentação conhece; por isso reexporta o erro de domínio.
"""
from livraria.aplicacao.servicos import Servicos, criar_servicos
from livraria.dominio.excecoes import RegraInvalida

__all__ = ["RegraInvalida", "Servicos", "criar_servicos"]
