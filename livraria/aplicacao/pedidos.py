from livraria.aplicacao.base import Servico, exigir_cliente, preco_atual
from livraria.aplicacao.dto import Historico
from livraria.dominio import regras
from livraria.dominio.excecoes import RegraInvalida


class ServicoPedidos(Servico):
    """Reserva, cancelamento, retirada, compra direta e histórico (R05)."""

    def _debitar(self, uow, edicao_id, loja_id):
        if not uow.lojas.debitar(edicao_id, loja_id):
            raise RegraInvalida("Sem estoque nesta unidade/edição.")

    def _reserva_confirmada(self, uow, cliente_id, codigo):
        exigir_cliente(uow, cliente_id)
        reserva = uow.pedidos.reserva_do_cliente(cliente_id, codigo)
        if not reserva:
            raise RegraInvalida("Reserva inexistente, de outro cliente ou já finalizada.")
        return reserva

    def reservar(self, cliente_id, edicao_id, loja_id):
        with self.banco.transacao(imediata=True) as uow:
            exigir_cliente(uow, cliente_id)
            preco = preco_atual(uow, edicao_id)
            self._debitar(uow, edicao_id, loja_id)
            identificador = uow.pedidos.criar_reserva(cliente_id, edicao_id, loja_id, preco)
            uow.pedidos.definir_codigo(identificador, regras.codigo_reserva(identificador))
            return uow.pedidos.obter_reserva(identificador)

    def cancelar(self, cliente_id, codigo):
        with self.banco.transacao(imediata=True) as uow:
            reserva = self._reserva_confirmada(uow, cliente_id, codigo)
            reserva.cancelar()
            uow.pedidos.atualizar_estado(reserva)
            uow.lojas.creditar(reserva.edicao_id, reserva.loja_id)

    def retirar(self, cliente_id, codigo):
        with self.banco.transacao(imediata=True) as uow:
            reserva = self._reserva_confirmada(uow, cliente_id, codigo)
            reserva.retirar()
            uow.pedidos.atualizar_estado(reserva)
            return uow.pedidos.criar_compra(cliente_id, reserva.edicao_id, reserva.loja_id,
                                            reserva.preco_centavos, reserva.id)

    def comprar(self, cliente_id, edicao_id, loja_id):
        with self.banco.transacao(imediata=True) as uow:
            exigir_cliente(uow, cliente_id)
            preco = preco_atual(uow, edicao_id)
            self._debitar(uow, edicao_id, loja_id)
            return uow.pedidos.criar_compra(cliente_id, edicao_id, loja_id, preco)

    def historico(self, cliente_id):
        with self.banco.transacao() as uow:
            exigir_cliente(uow, cliente_id)
            compras = uow.pedidos.compras_do_cliente(cliente_id)
            return Historico(uow.pedidos.reservas_do_cliente(cliente_id), compras, regras.pontos_fidelidade(compras))
