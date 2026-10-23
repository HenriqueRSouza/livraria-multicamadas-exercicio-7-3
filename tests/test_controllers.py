"""C01–C07 e C09 (docs/specs/livraria.md) testados nos controllers, com banco SQLite temporário."""
import tempfile
import unittest
from pathlib import Path

from db.db import Banco
from livraria.controllers import avaliacoes, catalogo, clientes, comunicacao, pedidos
from livraria.models import RegraInvalida


class ControllersTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.caminho = Path(self.tmp.name) / "teste.db"
        self.b = Banco(self.caminho)

    def cliente(self, email="ana@example.com"):
        return clientes.cadastrar(self.b, "Ana", email, "Centro", "Ficção")

    def test_c01_busca_combinada_e_sem_resultado(self):
        self.assertEqual(len(catalogo.buscar_livros(self.b)), 2)
        self.assertEqual([l["id"] for l in catalogo.buscar_livros(self.b, "mares", "ANDRADE", "ficcao")], [1])
        self.assertEqual(catalogo.buscar_livros(self.b, titulo="inexistente"), [])

    def test_c02_detalhes_e_preco_promocional(self):
        livro = catalogo.detalhes_livro(self.b, 1)
        self.assertEqual(len(livro["edicoes"]), 2)
        self.assertEqual(livro["edicoes"][0]["preco_final_centavos"], 4000)
        self.assertEqual({s["loja_id"]: s["quantidade"] for s in livro["edicoes"][0]["estoques"]}, {1: 1, 2: 2})
        with self.assertRaises(RegraInvalida):
            catalogo.detalhes_livro(self.b, 999)

    def test_c03_lojas_por_bairro_e_estoque_por_loja(self):
        self.assertEqual([l["nome"] for l in catalogo.listar_lojas(self.b, "CENTRO")], ["Unidade Centro"])
        self.assertEqual(catalogo.estoque(self.b, 1, 1)["secao"], "Literatura")
        self.assertEqual(catalogo.estoque(self.b, 1, 2)["quantidade"], 2)

    def test_c04_cadastro_favoritos_recomendacoes(self):
        for nome, email, bairro in (("", "ok@example.com", "Centro"), ("Ana", "ruim", "Centro"), ("Ana", "ok@example.com", "")):
            with self.assertRaises(RegraInvalida):
                clientes.cadastrar(self.b, nome, email, bairro)
        ana = self.cliente()
        with self.assertRaises(RegraInvalida):
            self.cliente("ANA@example.com")
        self.assertEqual([l["id"] for l in clientes.recomendacoes(self.b, ana)], [1])
        clientes.favorito(self.b, ana, 1)
        clientes.favorito(self.b, ana, 1)
        self.assertEqual(len(clientes.favoritos(self.b, ana)), 1)
        self.assertEqual(clientes.recomendacoes(self.b, ana), [])
        clientes.favorito(self.b, ana, 1, adicionar=False)
        self.assertEqual(clientes.favoritos(self.b, ana), [])
        self.assertTrue(any(n["tipo"] == "promocao" for n in clientes.notificacoes(self.b, ana)))

    def test_c05_reserva_ultimo_exemplar_e_cancelamento(self):
        ana = self.cliente()
        reserva = pedidos.reservar(self.b, ana, 1, 1)
        self.assertEqual((reserva["codigo"], reserva["estado"], reserva["preco_centavos"]), ("RES-000001", "confirmada", 4000))
        self.assertEqual(catalogo.estoque(self.b, 1, 1)["quantidade"], 0)
        self.assertEqual(catalogo.estoque(self.b, 1, 2)["quantidade"], 2)
        with self.assertRaises(RegraInvalida):
            pedidos.reservar(self.b, ana, 1, 1)
        pedidos.cancelar(self.b, ana, "RES-000001")
        self.assertEqual(catalogo.estoque(self.b, 1, 1)["quantidade"], 1)
        with self.assertRaises(RegraInvalida):
            pedidos.cancelar(self.b, ana, "RES-000001")

    def test_c06_retirada_compra_direta_e_pontos(self):
        ana, bia = self.cliente(), self.cliente("bia@example.com")
        pedidos.reservar(self.b, ana, 1, 1)
        with self.assertRaises(RegraInvalida):
            pedidos.retirar(self.b, bia, "RES-000001")
        pedidos.retirar(self.b, ana, "RES-000001")
        with self.assertRaises(RegraInvalida):
            pedidos.retirar(self.b, ana, "RES-000001")
        self.assertEqual(catalogo.estoque(self.b, 1, 1)["quantidade"], 0)
        self.assertEqual(pedidos.comprar(self.b, ana, 1, 2)["preco_centavos"], 4000)
        with self.assertRaises(RegraInvalida):
            pedidos.comprar(self.b, ana, 2, 1)
        historico = pedidos.historico(self.b, ana)
        self.assertEqual((len(historico["compras"]), historico["pontos"]), (2, 80))

    def test_c07_alerta_reposicao_e_persistencia(self):
        ana = self.cliente()
        comunicacao.alertar(self.b, ana, 2, 1)
        comunicacao.alertar(self.b, ana, 2, 1)
        with self.assertRaises(RegraInvalida):
            comunicacao.alertar(self.b, ana, 1, 1)
        comunicacao.repor(self.b, 2, 1)
        self.assertEqual(sum(n["tipo"] == "reposicao" for n in clientes.notificacoes(self.b, ana)), 1)
        self.assertEqual(catalogo.estoque(Banco(self.caminho), 2, 1)["quantidade"], 1)

    def test_c09_avaliacao_media_e_substituicao(self):
        ana = self.cliente()
        self.assertEqual(catalogo.detalhes_livro(self.b, 1)["media_avaliacoes"], 5.0)
        avaliacoes.avaliar(self.b, ana, 1, "4", "  Gostei do final.  ")
        livro = catalogo.detalhes_livro(self.b, 1)
        self.assertEqual((livro["media_avaliacoes"], livro["total_avaliacoes"]), (4.5, 2))
        avaliacoes.avaliar(self.b, ana, 1, 2)
        self.assertEqual(catalogo.detalhes_livro(self.b, 1)["total_avaliacoes"], 2)
        self.assertEqual([(a["titulo"], a["nota"]) for a in avaliacoes.avaliacoes_do_cliente(self.b, ana)], [("A Casa das Marés", 2)])

    def test_c09_avaliacao_invalida_nao_grava(self):
        ana = self.cliente()
        for livro_id, nota, texto in ((1, 0, ""), (1, 6, ""), (1, "cinco", ""), (1, 3, "x" * 501), (999, 3, "")):
            with self.assertRaises(RegraInvalida):
                avaliacoes.avaliar(self.b, ana, livro_id, nota, texto)
        self.assertEqual(catalogo.detalhes_livro(self.b, 1)["total_avaliacoes"], 1)


if __name__ == "__main__":
    unittest.main()
