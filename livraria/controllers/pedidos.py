from db import db
from livraria.models import RegraInvalida, Reserva, pontos, preco_final

from .clientes import carregar_cliente


def _preco(con, edicao_id):
    edicao = db.edicao(con, edicao_id)
    if not edicao:
        raise RegraInvalida("Edição inválida.")
    return preco_final(edicao["preco_centavos"], db.promocoes_ativas(con, edicao_id))


def _debitar(con, edicao_id, loja_id):
    item = db.estoque(con, edicao_id, loja_id)
    if not item or item["quantidade"] == 0:
        raise RegraInvalida("Sem estoque nesta unidade/edição.")
    db.alterar_estoque(con, edicao_id, loja_id, item["quantidade"] - 1)


def reservar(banco, cliente_id, edicao_id, loja_id):
    with banco.conexao(transacao=True) as con:
        carregar_cliente(con, cliente_id)
        preco = _preco(con, edicao_id)
        _debitar(con, edicao_id, loja_id)
        return db.inserir_reserva(con, cliente_id, edicao_id, loja_id, preco)


def comprar(banco, cliente_id, edicao_id, loja_id):
    with banco.conexao(transacao=True) as con:
        carregar_cliente(con, cliente_id)
        preco = _preco(con, edicao_id)
        _debitar(con, edicao_id, loja_id)
        return db.inserir_compra(con, cliente_id, edicao_id, loja_id, preco)


def _reserva(con, codigo):
    dados = db.reserva_por_codigo(con, codigo)
    if not dados:
        raise RegraInvalida("Reserva inexistente, de outro cliente ou já finalizada.")
    return dados, Reserva(dados["id"], dados["cliente_id"], dados["estado"])


def cancelar(banco, cliente_id, codigo):
    with banco.conexao(transacao=True) as con:
        dados, reserva = _reserva(con, codigo)
        reserva.cancelar(cliente_id)
        db.alterar_estado_reserva(con, reserva.id, reserva.estado)
        item = db.estoque(con, dados["edicao_id"], dados["loja_id"])
        db.alterar_estoque(con, dados["edicao_id"], dados["loja_id"], item["quantidade"] + 1)


def retirar(banco, cliente_id, codigo):
    with banco.conexao(transacao=True) as con:
        dados, reserva = _reserva(con, codigo)
        reserva.retirar(cliente_id)
        db.alterar_estado_reserva(con, reserva.id, reserva.estado)
        return db.inserir_compra(con, cliente_id, dados["edicao_id"], dados["loja_id"], dados["preco_centavos"], reserva.id)


def historico(banco, cliente_id):
    with banco.conexao() as con:
        carregar_cliente(con, cliente_id)
        compras = db.compras_do_cliente(con, cliente_id)
        return {"reservas": db.reservas_do_cliente(con, cliente_id), "compras": compras, "pontos": pontos(compras)}
