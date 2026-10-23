from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from livraria.apresentacao.suporte import cliente_id, logado, servicos

bp = Blueprint("cliente", __name__)


@bp.get("/cliente")
def area():
    if not session.get("cliente_id"):
        return render_template("entrada.html")
    s, atual = servicos(), cliente_id()
    return render_template("cliente.html", historico=s.pedidos.historico(atual),
                           favoritos=s.clientes.favoritos(atual), recomendacoes=s.clientes.recomendacoes(atual),
                           notificacoes=s.comunicacao.notificacoes(atual))


@bp.post("/cadastro")
def cadastro():
    form = request.form
    session["cliente_id"] = servicos().clientes.cadastrar(form.get("nome", ""), form.get("email", ""),
                                                          form.get("bairro", ""), form.get("interesses", ""))
    flash("Cadastro concluído. Esta é uma sessão local de demonstração.")
    return redirect(url_for("cliente.area"))


@bp.post("/entrar")
def entrar():
    session["cliente_id"] = servicos().clientes.cliente_por_email(request.form.get("email", "")).id
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
    servicos().clientes.favorito(cliente_id(), livro_id, acao == "adicionar")
    return redirect(url_for("catalogo.livro", livro_id=livro_id) if acao == "adicionar" else url_for("cliente.area"))
