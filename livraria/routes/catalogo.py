from flask import Blueprint, render_template, request

from livraria.controllers import catalogo

from . import banco

bp = Blueprint("catalogo", __name__)


@bp.get("/")
def inicio():
    livros = catalogo.buscar_livros(banco(), request.args.get("titulo", ""), request.args.get("autor", ""), request.args.get("genero", ""))
    return render_template("catalogo.html", livros=livros)


@bp.get("/livro/<int:livro_id>")
def livro(livro_id):
    return render_template("livro.html", livro=catalogo.detalhes_livro(banco(), livro_id))


@bp.get("/lojas")
def lojas():
    return render_template("lojas.html", lojas=catalogo.listar_lojas(banco(), request.args.get("bairro", "")))
