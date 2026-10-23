from db import db
from livraria.models import RegraInvalida

from .clientes import carregar_cliente


def alertar(banco, cliente_id, edicao_id, loja_id):
    with banco.conexao() as con:
        carregar_cliente(con, cliente_id)
        item = db.estoque(con, edicao_id, loja_id)
        if not item or item["quantidade"] != 0:
            raise RegraInvalida("Alerta permitido apenas para edição esgotada na unidade.")
        db.adicionar_alerta(con, cliente_id, edicao_id, loja_id)


def repor(banco, edicao_id, loja_id):
    """Reposição simulada: +1 no estoque e notificação local para quem pediu alerta."""
    with banco.conexao(transacao=True) as con:
        item = db.estoque(con, edicao_id, loja_id)
        if not item:
            raise RegraInvalida("Edição ou loja inválida.")
        db.alterar_estoque(con, edicao_id, loja_id, item["quantidade"] + 1)
        for cliente_id in db.consumir_alertas(con, edicao_id, loja_id):
            db.notificar(con, cliente_id, "reposicao", f"Reposição simulada: {item['titulo']} em {item['loja_nome']}")
