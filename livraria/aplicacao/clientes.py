from livraria.aplicacao.base import Servico, exigir_cliente
from livraria.dominio import regras
from livraria.dominio.excecoes import RegraInvalida


class ServicoClientes(Servico):
    def cadastrar(self, nome, email, bairro, interesses=""):
        nome, email, bairro, interesses = regras.validar_cadastro(nome, email, bairro, interesses)
        with self.banco.transacao(imediata=True) as uow:
            if uow.clientes.por_email(email):
                raise RegraInvalida("Email já cadastrado.")
            cliente = uow.clientes.inserir(nome, email, bairro, interesses)
            for promocao, genero in uow.edicoes.promocoes_ativas_com_genero():
                if regras.tem_interesse(cliente, genero):
                    uow.clientes.notificar(cliente.id, "promocao", promocao.descricao)
            return cliente.id

    def cliente_por_email(self, email):
        with self.banco.transacao() as uow:
            cliente = uow.clientes.por_email(email.strip())
            if not cliente:
                raise RegraInvalida("Email não cadastrado.")
            return cliente

    def cliente(self, cliente_id):
        with self.banco.transacao() as uow:
            return exigir_cliente(uow, cliente_id)

    def favorito(self, cliente_id, livro_id, adicionar=True):
        with self.banco.transacao() as uow:
            exigir_cliente(uow, cliente_id)
            if not uow.livros.obter(livro_id):
                raise RegraInvalida("Livro inválido.")
            if adicionar:
                uow.clientes.adicionar_favorito(cliente_id, livro_id)
            else:
                uow.clientes.remover_favorito(cliente_id, livro_id)

    def favoritos(self, cliente_id):
        with self.banco.transacao() as uow:
            exigir_cliente(uow, cliente_id)
            return uow.clientes.favoritos(cliente_id)

    def recomendacoes(self, cliente_id):
        with self.banco.transacao() as uow:
            cliente = exigir_cliente(uow, cliente_id)
            favoritos = {b.id for b in uow.clientes.favoritos(cliente_id)}
            return regras.recomendar(cliente, uow.livros.listar(), favoritos)
