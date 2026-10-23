from livraria.dominio.excecoes import RegraInvalida
from livraria.dominio.regras import preco_final


class Servico:
    def __init__(self, banco):
        self.banco = banco


def exigir_cliente(uow, cliente_id):
    cliente = uow.clientes.obter(cliente_id)
    if not cliente:
        raise RegraInvalida("Cliente inválido; cadastre-se primeiro.")
    return cliente


def preco_atual(uow, edicao_id):
    """R02: preço vigente da edição, congelado por quem o registra."""
    edicao = uow.edicoes.obter(edicao_id)
    if not edicao:
        raise RegraInvalida("Edição inválida.")
    return preco_final(edicao.preco_centavos, uow.edicoes.promocoes_ativas(edicao_id))
