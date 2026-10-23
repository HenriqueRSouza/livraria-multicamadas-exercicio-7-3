from db import db
from livraria.models import Cliente, RegraInvalida, recomendar


def carregar_cliente(con, cliente_id):
    dados = db.cliente(con, cliente_id)
    if not dados:
        raise RegraInvalida("Cliente inválido; cadastre-se primeiro.")
    return dados


def cadastrar(banco, nome, email, bairro, interesses=""):
    cliente = Cliente(nome, email, bairro, interesses)
    with banco.conexao() as con:
        cliente_id = db.inserir_cliente(con, cliente.nome, cliente.email, cliente.bairro, cliente.interesses)
        if cliente_id is None:
            raise RegraInvalida("Email já cadastrado.")
        for promo in db.promocoes_ativas(con):
            if cliente.interessado_em(promo["genero"]):
                db.notificar(con, cliente_id, "promocao", promo["descricao"])
        return cliente_id


def entrar(banco, email):
    with banco.conexao() as con:
        dados = db.cliente_por_email(con, email.strip())
    if not dados:
        raise RegraInvalida("Email não cadastrado.")
    return dados["id"]


def cliente(banco, cliente_id):
    with banco.conexao() as con:
        return carregar_cliente(con, cliente_id)


def favorito(banco, cliente_id, livro_id, adicionar=True):
    with banco.conexao() as con:
        carregar_cliente(con, cliente_id)
        if not db.livro(con, livro_id):
            raise RegraInvalida("Livro inválido.")
        if adicionar:
            db.adicionar_favorito(con, cliente_id, livro_id)
        else:
            db.remover_favorito(con, cliente_id, livro_id)


def favoritos(banco, cliente_id):
    with banco.conexao() as con:
        carregar_cliente(con, cliente_id)
        return db.favoritos(con, cliente_id)


def recomendacoes(banco, cliente_id):
    with banco.conexao() as con:
        dados = carregar_cliente(con, cliente_id)
        cliente = Cliente(dados["nome"], dados["email"], dados["bairro"], dados["interesses"])
        return recomendar(cliente, db.livros(con), db.favoritos(con, cliente_id))


def notificacoes(banco, cliente_id):
    with banco.conexao() as con:
        carregar_cliente(con, cliente_id)
        return db.notificacoes(con, cliente_id)
