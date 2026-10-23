from flask import Blueprint, flash, redirect, request, url_for

from livraria.apresentacao.suporte import cliente_id, ids_estoque, logado, servicos

bp = Blueprint("comunicacao", __name__)


@bp.post("/alertar")
@logado
def alertar():
    servicos().comunicacao.alertar(cliente_id(), *ids_estoque())
    flash("Alerta local registrado; consulte sua área após simular reposição.")
    return redirect(request.referrer or url_for("catalogo.inicio"))


@bp.post("/repor")
def repor():
    servicos().comunicacao.repor(*ids_estoque())
    flash("Reposição simulada: uma unidade adicionada e notificações locais geradas.")
    return redirect(request.referrer or url_for("catalogo.inicio"))
