"""Utilidades compartilhadas pelas rotas."""
from functools import wraps

from flask import current_app, flash, redirect, request, session, url_for

EXTENSAO = "livraria"


def servicos():
    return current_app.extensions[EXTENSAO]


def cliente_id():
    return session["cliente_id"]


def ids_estoque():
    """Lê edição e loja enviadas pelos formulários de estoque."""
    return int(request.form["edicao_id"]), int(request.form["loja_id"])


def logado(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("cliente_id"):
            flash("Cadastre-se ou entre para continuar.", "erro")
            return redirect(url_for("cliente.area"))
        return fn(*args, **kwargs)
    return wrapper
