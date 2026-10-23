"""Composição dos serviços sobre um banco SQLite."""
from dataclasses import dataclass

from livraria.aplicacao.catalogo import ServicoCatalogo
from livraria.aplicacao.clientes import ServicoClientes
from livraria.aplicacao.comunicacao import ServicoComunicacao
from livraria.aplicacao.lojas import ServicoLojas
from livraria.aplicacao.pedidos import ServicoPedidos
from livraria.dados import BancoSQLite


@dataclass
class Servicos:
    catalogo: ServicoCatalogo
    lojas: ServicoLojas
    clientes: ServicoClientes
    pedidos: ServicoPedidos
    comunicacao: ServicoComunicacao


def criar_servicos(caminho_banco):
    """Inicializa o banco (idempotente) e devolve os serviços prontos para uso."""
    banco = BancoSQLite(caminho_banco)
    banco.inicializar()
    return Servicos(ServicoCatalogo(banco), ServicoLojas(banco), ServicoClientes(banco),
                    ServicoPedidos(banco), ServicoComunicacao(banco))
