"""Nova feature: avaliações de clientes (R07)."""
from db import db
from livraria.models import Avaliacao, RegraInvalida

from .clientes import carregar_cliente


def avaliar(banco, cliente_id, livro_id, nota, texto=""):
    avaliacao = Avaliacao(nota, texto)
    with banco.conexao() as con:
        cliente = carregar_cliente(con, cliente_id)
        if not db.livro(con, livro_id):
            raise RegraInvalida("Livro não encontrado.")
        db.salvar_avaliacao(con, livro_id, cliente_id, avaliacao.nota, avaliacao.texto, cliente["nome"])
    return avaliacao


def avaliacoes_do_cliente(banco, cliente_id):
    with banco.conexao() as con:
        carregar_cliente(con, cliente_id)
        return db.avaliacoes_do_cliente(con, cliente_id)
