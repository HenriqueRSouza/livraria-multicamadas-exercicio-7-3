from flask import Blueprint, flash, redirect, request, url_for

from livraria.controllers import comunicacao

from . import banco, cliente_id, ids_estoque, logado

bp = Blueprint("comunicacao", __name__)


@bp.post("/alertar")
@logado
def alertar():
    comunicacao.alertar(banco(), cliente_id(), *ids_estoque())
    flash("Alerta local registrado; consulte sua área após simular reposição.")
    return redirect(request.referrer or url_for("catalogo.inicio"))


@bp.post("/repor")
def repor():
    comunicacao.repor(banco(), *ids_estoque())
    flash("Reposição simulada: uma unidade adicionada e notificações locais geradas.")
    return redirect(request.referrer or url_for("catalogo.inicio"))
