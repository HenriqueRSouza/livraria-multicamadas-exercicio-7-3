"""C08 e C09 via HTTP: testa as rotas (apresentação) passando por todas as camadas."""
import tempfile
import unittest
from pathlib import Path

from app import create_app


class FluxoHTTPTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.app = create_app(str(Path(self.tmp.name) / "site.db"))
        self.app.testing = True
        self.web = self.app.test_client()

    def test_c08_catalogo_detalhes_estoque_reserva_retirada(self):
        self.assertIn("A Casa das Marés", self.web.get("/?titulo=mares").text)
        self.assertIn("Seção Literatura", self.web.get("/livro/1").text)
        self.assertIn("Unidade Centro", self.web.get("/lojas?bairro=centro").text)
        self.assertNotIn("Unidade Jardim", self.web.get("/lojas?bairro=centro").text)
        self.web.post("/cadastro", data={"nome": "Ana", "email": "ana@example.com", "bairro": "Centro", "interesses": "Ficção"})
        resposta = self.web.post("/reservar", data={"edicao_id": 1, "loja_id": 1}, follow_redirects=True)
        self.assertIn("RES-000001", resposta.text)
        self.assertIn("Seção Literatura", resposta.text)
        self.assertIn("0 disponível(is)", self.web.get("/livro/1").text)
        resposta = self.web.post("/reserva/RES-000001/retirar", follow_redirects=True)
        self.assertIn("40 pontos", resposta.text)
        self.assertIn("retirada", resposta.text)
        self.assertIn("#1", resposta.text)

    def test_c08_favoritos_alerta_reposicao_compra_e_erros(self):
        self.web.post("/cadastro", data={"nome": "Ana", "email": "ana@example.com", "bairro": "Centro", "interesses": "Ficção"})
        self.web.post("/favorito/1/adicionar")
        self.assertIn("A Casa das Marés", self.web.get("/cliente").text)
        self.web.post("/favorito/1/remover")
        self.web.post("/alertar", data={"edicao_id": 2, "loja_id": 1})
        self.web.post("/repor", data={"edicao_id": 2, "loja_id": 1})
        self.assertIn("Reposição simulada", self.web.get("/cliente").text)
        self.web.post("/comprar", data={"edicao_id": 2, "loja_id": 1})
        self.assertIn("75 pontos", self.web.get("/cliente").text)
        resposta = self.web.post("/comprar", data={"edicao_id": 2, "loja_id": 1}, follow_redirects=True)
        self.assertIn("Sem estoque", resposta.text)

    def test_c09_avaliar_livro_pela_interface(self):
        self.assertNotIn("Enviar avaliação", self.web.get("/livro/1").text)
        self.web.post("/livro/1/avaliar", data={"nota": "4"})
        self.assertEqual(self.web.get("/livro/1").status_code, 200)
        self.web.post("/cadastro", data={"nome": "Ana", "email": "ana@example.com", "bairro": "Centro", "interesses": "Ficção"})
        self.assertIn("Média 5,0/5", self.web.get("/livro/1").text)
        resposta = self.web.post("/livro/1/avaliar", data={"nota": "4", "texto": "Gostei"}, follow_redirects=True)
        self.assertIn("Avaliação registrada: 4/5", resposta.text)
        self.assertIn("Média 4,5/5", resposta.text)
        self.assertIn("2 avaliação(ões)", resposta.text)
        self.assertIn("A Casa das Marés</a> · 4/5 — Gostei", self.web.get("/cliente").text)
        resposta = self.web.post("/livro/1/avaliar", data={"nota": "9"}, headers={"Referer": "/livro/1"}, follow_redirects=True)
        self.assertIn("nota deve ser", resposta.text)


if __name__ == "__main__":
    unittest.main()
