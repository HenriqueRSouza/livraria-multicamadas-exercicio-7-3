"""Camada de Apresentação: rotas Flask. Leem o request, chamam um controller e devolvem a página."""
from functools import wraps

from flask import current_app, flash, redirect, request, session, url_for


def banco():
    return current_app.config["BANCO"]


def cliente_id():
    return session.get("cliente_id")


def ids_estoque():
    return int(request.form["edicao_id"]), int(request.form["loja_id"])


def logado(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not cliente_id():
            flash("Cadastre-se ou entre para continuar.", "erro")
            return redirect(url_for("cliente.area"))
        return fn(*args, **kwargs)
    return wrapper
