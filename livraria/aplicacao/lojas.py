from livraria.aplicacao.base import Servico
from livraria.dominio import regras
from livraria.dominio.excecoes import RegraInvalida


class ServicoLojas(Servico):
    def listar_lojas(self, bairro=""):
        with self.banco.transacao() as uow:
            return [l for l in uow.lojas.listar() if regras.normalizar(bairro) in regras.normalizar(l.bairro)]

    def estoque(self, edicao_id, loja_id):
        with self.banco.transacao() as uow:
            item = uow.lojas.estoque(edicao_id, loja_id)
            if not item:
                raise RegraInvalida("Edição ou loja inválida.")
            return item
