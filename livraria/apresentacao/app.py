"""Fábrica da aplicação Flask."""
import os

from flask import Flask, flash, redirect, request, session, url_for

from livraria.aplicacao import RegraInvalida, criar_servicos
from livraria.apresentacao import rotas_catalogo, rotas_cliente, rotas_comunicacao, rotas_pedidos
from livraria.apresentacao.suporte import EXTENSAO, servicos


def create_app(db_path=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("LIVRARIA_SECRET", "chave-local-apenas-demonstracao")
    app.extensions[EXTENSAO] = criar_servicos(db_path or os.environ.get("LIVRARIA_DB", "livraria.db"))

    for modulo in (rotas_catalogo, rotas_cliente, rotas_pedidos, rotas_comunicacao):
        app.register_blueprint(modulo.bp)

    @app.template_filter("reais")
    def reais(centavos):
        return f"R$ {centavos / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @app.errorhandler(RegraInvalida)
    def erro(exc):
        flash(str(exc), "erro")
        return redirect(request.referrer or url_for("catalogo.inicio"))

    @app.context_processor
    def contexto():
        cliente_id = session.get("cliente_id")
        return {"cliente_atual": servicos().clientes.cliente(cliente_id) if cliente_id else None}

    return app
