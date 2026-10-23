from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from livraria.controllers import avaliacoes, clientes, pedidos

from . import banco, cliente_id, logado

bp = Blueprint("cliente", __name__)


@bp.get("/cliente")
def area():
    if not cliente_id():
        return render_template("entrada.html")
    b, atual = banco(), cliente_id()
    return render_template("cliente.html", historico=pedidos.historico(b, atual), favoritos=clientes.favoritos(b, atual),
                           recomendacoes=clientes.recomendacoes(b, atual), notificacoes=clientes.notificacoes(b, atual),
                           avaliacoes=avaliacoes.avaliacoes_do_cliente(b, atual))


@bp.post("/cadastro")
def cadastro():
    f = request.form
    session["cliente_id"] = clientes.cadastrar(banco(), f.get("nome", ""), f.get("email", ""), f.get("bairro", ""), f.get("interesses", ""))
    flash("Cadastro concluído. Esta é uma sessão local de demonstração.")
    return redirect(url_for("cliente.area"))


@bp.post("/entrar")
def entrar():
    session["cliente_id"] = clientes.entrar(banco(), request.form.get("email", ""))
    return redirect(url_for("cliente.area"))


@bp.post("/sair")
def sair():
    session.clear()
    return redirect(url_for("catalogo.inicio"))


@bp.post("/favorito/<int:livro_id>/<acao>")
@logado
def favorito(livro_id, acao):
    if acao not in ("adicionar", "remover"):
        abort(404)
    clientes.favorito(banco(), cliente_id(), livro_id, acao == "adicionar")
    return redirect(url_for("catalogo.livro", livro_id=livro_id) if acao == "adicionar" else url_for("cliente.area"))
