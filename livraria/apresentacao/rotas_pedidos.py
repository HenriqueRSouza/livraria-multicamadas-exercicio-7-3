from flask import Blueprint, abort, flash, redirect, url_for

from livraria.apresentacao.suporte import cliente_id, ids_estoque, logado, servicos

bp = Blueprint("pedidos", __name__)


@bp.post("/reservar")
@logado
def reservar():
    reserva = servicos().pedidos.reservar(cliente_id(), *ids_estoque())
    flash(f"Reserva confirmada: {reserva.codigo}. Retire na unidade selecionada; pagamento simulado apenas na retirada.")
    return redirect(url_for("cliente.area"))


@bp.post("/comprar")
@logado
def comprar():
    compra = servicos().pedidos.comprar(cliente_id(), *ids_estoque())
    flash(f"Compra presencial simulada registrada: #{compra.id} (sem cobrança real).")
    return redirect(url_for("cliente.area"))


@bp.post("/reserva/<codigo>/<acao>")
@logado
def reserva_acao(codigo, acao):
    if acao == "retirar":
        servicos().pedidos.retirar(cliente_id(), codigo)
        flash(f"Retirada de {codigo} concluída; compra simulada registrada.")
    elif acao == "cancelar":
        servicos().pedidos.cancelar(cliente_id(), codigo)
        flash(f"Reserva {codigo} cancelada; estoque devolvido.")
    else:
        abort(404)
    return redirect(url_for("cliente.area"))
