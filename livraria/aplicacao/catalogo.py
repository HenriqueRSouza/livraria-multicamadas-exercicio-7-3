from livraria.aplicacao.base import Servico
from livraria.aplicacao.dto import DetalheLivro, EdicaoDetalhada
from livraria.dominio import regras
from livraria.dominio.excecoes import RegraInvalida


class ServicoCatalogo(Servico):
    def buscar_livros(self, titulo="", autor="", genero=""):
        with self.banco.transacao() as uow:
            return [b for b in uow.livros.listar() if regras.corresponde(b, titulo, autor, genero)]

    def detalhes_livro(self, livro_id):
        with self.banco.transacao() as uow:
            livro = uow.livros.obter(livro_id)
            if not livro:
                raise RegraInvalida("Livro não encontrado.")
            edicoes = []
            for ed in uow.edicoes.por_livro(livro_id):
                promocoes = uow.edicoes.promocoes_ativas(ed.id)
                edicoes.append(EdicaoDetalhada(ed.id, ed.nome, ed.ano, ed.preco_centavos,
                                               regras.preco_final(ed.preco_centavos, promocoes),
                                               promocoes, uow.lojas.estoques_da_edicao(ed.id)))
            avaliacoes = uow.livros.avaliacoes(livro_id)
            return DetalheLivro(livro.id, livro.titulo, livro.autor, livro.genero, livro.sinopse, avaliacoes,
                                edicoes, regras.media_avaliacoes(avaliacoes), len(avaliacoes))
