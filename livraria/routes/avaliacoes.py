from flask import Blueprint, flash, redirect, request, url_for

from livraria.controllers import avaliacoes

from . import banco, cliente_id, logado

bp = Blueprint("avaliacoes", __name__)


@bp.post("/livro/<int:livro_id>/avaliar")
@logado
def avaliar(livro_id):
    avaliacao = avaliacoes.avaliar(banco(), cliente_id(), livro_id, request.form.get("nota"), request.form.get("texto", ""))
    flash(f"Avaliação registrada: {avaliacao.nota}/5.")
    return redirect(url_for("catalogo.livro", livro_id=livro_id))
