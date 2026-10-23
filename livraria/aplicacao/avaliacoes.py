from livraria.aplicacao.base import Servico, exigir_cliente
from livraria.dominio import regras
from livraria.dominio.excecoes import RegraInvalida


class ServicoAvaliacoes(Servico):
    """Avaliações de clientes (R07)."""

    def avaliar(self, cliente_id, livro_id, nota, texto=""):
        nota, texto = regras.validar_avaliacao(nota, texto)
        with self.banco.transacao(imediata=True) as uow:
            cliente = exigir_cliente(uow, cliente_id)
            if not uow.livros.obter(livro_id):
                raise RegraInvalida("Livro inválido.")
            return uow.livros.salvar_avaliacao(cliente, livro_id, nota, texto)

    def avaliacoes_do_cliente(self, cliente_id):
        with self.banco.transacao() as uow:
            exigir_cliente(uow, cliente_id)
            return uow.livros.avaliacoes_do_cliente(cliente_id)
