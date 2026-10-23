from flask import Blueprint, render_template, request

from livraria.apresentacao.suporte import servicos

bp = Blueprint("catalogo", __name__)


@bp.get("/")
def inicio():
    args = request.args
    return render_template("catalogo.html", livros=servicos().catalogo.buscar_livros(
        args.get("titulo", ""), args.get("autor", ""), args.get("genero", "")))


@bp.get("/livro/<int:livro_id>")
def livro(livro_id):
    return render_template("livro.html", livro=servicos().catalogo.detalhes_livro(livro_id))


@bp.get("/lojas")
def lojas():
    return render_template("lojas.html", lojas=servicos().lojas.listar_lojas(request.args.get("bairro", "")))
