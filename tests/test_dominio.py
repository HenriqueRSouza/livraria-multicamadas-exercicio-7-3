"""Regras puras do domínio, sem banco nem Flask."""
import unittest

from livraria.dominio import Avaliacao, Cliente, Livro, Promocao, RegraInvalida, Reserva, regras


class RegrasTest(unittest.TestCase):
    def test_preco_final_nunca_negativo_e_ignora_promocao_inativa(self):
        promos = [Promocao(1, 1, "a", 1000, True), Promocao(2, 1, "b", 9000, False)]
        self.assertEqual(regras.preco_final(5000, promos), 4000)
        self.assertEqual(regras.preco_final(500, promos), 0)

    def test_busca_sem_caixa_e_acentos(self):
        livro = Livro(1, "A Casa das Marés", "L. Andrade", "Ficção", "")
        self.assertTrue(regras.corresponde(livro, titulo="MARES", genero="ficcao"))
        self.assertFalse(regras.corresponde(livro, titulo="mares", autor="ribeiro"))

    def test_cadastro_normaliza_e_valida(self):
        self.assertEqual(regras.validar_cadastro(" Ana ", " ANA@Ex.com ", " Centro ", "Ficção, ,Tecnologia"),
                         ("Ana", "ana@ex.com", "Centro", "Ficção,Tecnologia"))
        with self.assertRaises(RegraInvalida):
            regras.validar_cadastro("Ana", "ana@ex", "Centro")

    def test_transicoes_de_reserva(self):
        reserva = Reserva(1, 1, 1, 1, "RES-000001", "confirmada", 4000)
        reserva.retirar()
        self.assertEqual(reserva.estado, "retirada")
        for acao in (reserva.retirar, reserva.cancelar):
            with self.assertRaises(RegraInvalida):
                acao()

    def test_recomendacoes_pontos_e_codigo(self):
        cliente = Cliente(1, "Ana", "a@b.co", "Centro", "Ficção")
        livros = [Livro(2, "B", "x", "ficcao", ""), Livro(1, "A", "y", "Ficção", ""), Livro(3, "C", "z", "Tecnologia", "")]
        self.assertEqual([b.id for b in regras.recomendar(cliente, livros, {2})], [1])
        self.assertEqual(regras.codigo_reserva(7), "RES-000007")
        self.assertEqual(regras.pontos_fidelidade([Reserva(1, 1, 1, 1, None, "retirada", 4099)]), 40)

    def test_validar_avaliacao_e_media(self):
        self.assertEqual(regras.validar_avaliacao("5", "  ótimo "), (5, "ótimo"))
        for nota, texto in ((0, ""), (6, ""), ("x", ""), (3, "a" * 501)):
            with self.assertRaises(RegraInvalida):
                regras.validar_avaliacao(nota, texto)
        notas = [Avaliacao(i, 1, n, "", "x") for i, n in enumerate((5, 4, 4), 1)]
        self.assertEqual(regras.media_avaliacoes(notas), 4.3)
        self.assertIsNone(regras.media_avaliacoes([]))


if __name__ == "__main__":
    unittest.main()
