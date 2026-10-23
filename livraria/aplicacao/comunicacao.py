from livraria.aplicacao.base import Servico, exigir_cliente
from livraria.dominio import regras
from livraria.dominio.excecoes import RegraInvalida


class ServicoComunicacao(Servico):
    """Alertas de reposição e notificações locais (R06)."""

    def notificacoes(self, cliente_id):
        with self.banco.transacao() as uow:
            exigir_cliente(uow, cliente_id)
            return uow.clientes.notificacoes(cliente_id)

    def alertar(self, cliente_id, edicao_id, loja_id):
        with self.banco.transacao() as uow:
            exigir_cliente(uow, cliente_id)
            regras.exigir_esgotado(uow.lojas.estoque(edicao_id, loja_id))
            uow.clientes.registrar_alerta(cliente_id, edicao_id, loja_id)

    def repor(self, edicao_id, loja_id):
        with self.banco.transacao(imediata=True) as uow:
            estoque = uow.lojas.estoque(edicao_id, loja_id)
            if not estoque:
                raise RegraInvalida("Edição ou loja inválida.")
            livro = uow.livros.obter(uow.edicoes.obter(edicao_id).livro_id)
            uow.lojas.creditar(edicao_id, loja_id)
            for cliente_id in uow.clientes.consumir_alertas(edicao_id, loja_id):
                uow.clientes.notificar(cliente_id, "reposicao", f"Reposição simulada: {livro.titulo} em {estoque.loja_nome}")
