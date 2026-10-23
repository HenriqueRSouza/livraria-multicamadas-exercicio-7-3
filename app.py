"""Ponto de entrada: cria o app Flask, liga o banco e registra as rotas de cada camada."""
import os

from flask import Flask, flash, redirect, request, session, url_for

from db.db import Banco
from livraria.controllers import clientes
from livraria.models import RegraInvalida
from livraria.routes import avaliacoes, catalogo, cliente, comunicacao, pedidos


def create_app(db_path=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("LIVRARIA_SECRET", "chave-local-apenas-demonstracao")
    app.config["BANCO"] = Banco(db_path or os.environ.get("LIVRARIA_DB", "livraria.db"))
    for rotas in (catalogo, cliente, pedidos, comunicacao, avaliacoes):
        app.register_blueprint(rotas.bp)

    @app.template_filter("reais")
    def reais(centavos):
        return f"R$ {centavos / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @app.errorhandler(RegraInvalida)
    def erro(exc):
        flash(str(exc), "erro")
        return redirect(request.referrer or url_for("catalogo.inicio"))

    @app.context_processor
    def cliente_atual():
        cliente_id = session.get("cliente_id")
        return {"cliente_atual": clientes.cliente(app.config["BANCO"], cliente_id) if cliente_id else None}

    return app


if __name__ == "__main__":
    create_app().run(debug=False)
