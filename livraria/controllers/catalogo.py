from db import db
from livraria.models import RegraInvalida, combina_busca, media, normalizar, preco_final


def buscar_livros(banco, titulo="", autor="", genero=""):
    with banco.conexao() as con:
        return [b for b in db.livros(con) if combina_busca(b, titulo, autor, genero)]


def detalhes_livro(banco, livro_id):
    with banco.conexao() as con:
        livro = db.livro(con, livro_id)
        if not livro:
            raise RegraInvalida("Livro não encontrado.")
        livro["avaliacoes"] = db.avaliacoes(con, livro_id)
        livro["media_avaliacoes"] = media(livro["avaliacoes"])
        livro["total_avaliacoes"] = len(livro["avaliacoes"])
        livro["edicoes"] = db.edicoes(con, livro_id)
        for ed in livro["edicoes"]:
            ed["promocoes"] = db.promocoes_ativas(con, ed["id"])
            ed["preco_final_centavos"] = preco_final(ed["preco_centavos"], ed["promocoes"])
            ed["estoques"] = db.estoques_da_edicao(con, ed["id"])
        return livro


def listar_lojas(banco, bairro=""):
    with banco.conexao() as con:
        return [loja for loja in db.lojas(con) if normalizar(bairro) in normalizar(loja["bairro"])]


def estoque(banco, edicao_id, loja_id):
    with banco.conexao() as con:
        item = db.estoque(con, edicao_id, loja_id)
    if not item:
        raise RegraInvalida("Edição ou loja inválida.")
    return item
