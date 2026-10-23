from flask import Blueprint, flash, redirect, request, url_for

from livraria.apresentacao.suporte import cliente_id, logado, servicos

bp = Blueprint("avaliacoes", __name__)


@bp.post("/livro/<int:livro_id>/avaliar")
@logado
def avaliar(livro_id):
    avaliacao = servicos().avaliacoes.avaliar(cliente_id(), livro_id, request.form.get("nota"), request.form.get("texto", ""))
    flash(f"Avaliação registrada: {avaliacao.nota}/5.")
    return redirect(url_for("catalogo.livro", livro_id=livro_id))
