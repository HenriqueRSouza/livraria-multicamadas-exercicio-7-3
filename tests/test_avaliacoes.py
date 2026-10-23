"""C09 — avaliações de clientes (R07), pela camada de aplicação."""
import tempfile
import unittest
from pathlib import Path

from livraria.aplicacao import RegraInvalida, criar_servicos


class AvaliacoesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.s = criar_servicos(str(Path(self.tmp.name) / "teste.db"))
        self.ana = self.s.clientes.cadastrar("Ana", "ana@example.com", "Centro", "Ficção")

    def test_c09_avaliacao_aparece_no_livro_e_na_area_com_media(self):
        self.assertEqual((self.s.catalogo.detalhes_livro(1).media_avaliacoes, self.s.catalogo.detalhes_livro(1).total_avaliacoes), (5.0, 1))
        avaliacao = self.s.avaliacoes.avaliar(self.ana, 1, "4", "  Gostei do final.  ")
        self.assertEqual((avaliacao.nota, avaliacao.texto, avaliacao.autor), (4, "Gostei do final.", "Ana"))
        livro = self.s.catalogo.detalhes_livro(1)
        self.assertEqual((livro.media_avaliacoes, livro.total_avaliacoes), (4.5, 2))
        minhas = self.s.avaliacoes.avaliacoes_do_cliente(self.ana)
        self.assertEqual([(a.titulo, a.nota) for a in minhas], [("A Casa das Marés", 4)])

    def test_c09_reenviar_substitui_avaliacao_do_mesmo_cliente(self):
        self.s.avaliacoes.avaliar(self.ana, 2, 2, "Básico")
        self.s.avaliacoes.avaliar(self.ana, 2, 5)
        livro = self.s.catalogo.detalhes_livro(2)
        self.assertEqual([(a.nota, a.texto) for a in livro.avaliacoes], [(5, "")])
        bia = self.s.clientes.cadastrar("Bia", "bia@example.com", "Jardim")
        self.s.avaliacoes.avaliar(bia, 2, 4)
        livro = self.s.catalogo.detalhes_livro(2)
        self.assertEqual((livro.media_avaliacoes, livro.total_avaliacoes), (4.5, 2))

    def test_c09_entradas_invalidas_nao_gravam(self):
        for livro_id, nota, texto in ((1, 0, ""), (1, 6, ""), (1, "cinco", ""), (1, None, ""), (1, 3, "x" * 501), (999, 3, "")):
            with self.assertRaises(RegraInvalida):
                self.s.avaliacoes.avaliar(self.ana, livro_id, nota, texto)
        with self.assertRaises(RegraInvalida):
            self.s.avaliacoes.avaliar(999, 1, 3)
        self.s.avaliacoes.avaliar(self.ana, 1, 3, "x" * 500)
        self.assertEqual(self.s.catalogo.detalhes_livro(1).total_avaliacoes, 2)
        self.assertEqual(self.s.catalogo.detalhes_livro(2).total_avaliacoes, 0)


if __name__ == "__main__":
    unittest.main()
