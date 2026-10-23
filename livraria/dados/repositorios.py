"""Repositórios SQLite: traduzem linhas em entidades do domínio."""
from livraria.dominio.entidades import (Cliente, Compra, Edicao, Estoque, Livro, Loja, Notificacao,
                                        Promocao, Avaliacao, Reserva)


def _uma(cls, row):
    return cls(**dict(row)) if row else None


def _todas(cls, rows):
    return [cls(**dict(r)) for r in rows]


class _Repositorio:
    def __init__(self, conexao):
        self.db = conexao


class LivroRepositorio(_Repositorio):
    def listar(self):
        return _todas(Livro, self.db.execute("SELECT * FROM livros ORDER BY id"))

    def obter(self, livro_id):
        return _uma(Livro, self.db.execute("SELECT * FROM livros WHERE id=?", (livro_id,)).fetchone())

    def avaliacoes(self, livro_id):
        return _todas(Avaliacao, self.db.execute("SELECT id, livro_id, nota, texto, autor FROM avaliacoes WHERE livro_id=? ORDER BY id", (livro_id,)))


class EdicaoRepositorio(_Repositorio):
    def por_livro(self, livro_id):
        return _todas(Edicao, self.db.execute("SELECT * FROM edicoes WHERE livro_id=? ORDER BY id", (livro_id,)))

    def obter(self, edicao_id):
        return _uma(Edicao, self.db.execute("SELECT * FROM edicoes WHERE id=?", (edicao_id,)).fetchone())

    def promocoes_ativas(self, edicao_id):
        return _todas(Promocao, self.db.execute("SELECT * FROM promocoes WHERE edicao_id=? AND ativa=1 ORDER BY id", (edicao_id,)))

    def promocoes_ativas_com_genero(self):
        """Pares (promoção, gênero do livro) usados para avisos no cadastro."""
        rows = self.db.execute("SELECT p.*, b.genero FROM promocoes p JOIN edicoes e ON e.id=p.edicao_id JOIN livros b ON b.id=e.livro_id WHERE p.ativa=1 ORDER BY p.id")
        return [(Promocao(**{k: r[k] for k in r.keys() if k != "genero"}), r["genero"]) for r in rows]


class LojaRepositorio(_Repositorio):
    def listar(self):
        return _todas(Loja, self.db.execute("SELECT * FROM lojas ORDER BY id"))

    def estoques_da_edicao(self, edicao_id):
        return _todas(Estoque, self.db.execute("SELECT e.*, l.nome AS loja_nome FROM estoques e JOIN lojas l ON l.id=e.loja_id WHERE e.edicao_id=? ORDER BY e.loja_id", (edicao_id,)))

    def estoque(self, edicao_id, loja_id):
        return _uma(Estoque, self.db.execute("SELECT e.*, l.nome AS loja_nome FROM estoques e JOIN lojas l ON l.id=e.loja_id WHERE e.edicao_id=? AND e.loja_id=?", (edicao_id, loja_id)).fetchone())

    def debitar(self, edicao_id, loja_id):
        """Retira uma unidade se houver; devolve False quando não há estoque."""
        return self.db.execute("UPDATE estoques SET quantidade=quantidade-1 WHERE edicao_id=? AND loja_id=? AND quantidade>0", (edicao_id, loja_id)).rowcount == 1

    def creditar(self, edicao_id, loja_id):
        self.db.execute("UPDATE estoques SET quantidade=quantidade+1 WHERE edicao_id=? AND loja_id=?", (edicao_id, loja_id))


class ClienteRepositorio(_Repositorio):
    def inserir(self, nome, email, bairro, interesses):
        identificador = self.db.execute("INSERT INTO clientes(nome,email,bairro,interesses) VALUES (?,?,?,?)", (nome, email, bairro, interesses)).lastrowid
        return self.obter(identificador)

    def obter(self, cliente_id):
        return _uma(Cliente, self.db.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,)).fetchone())

    def por_email(self, email):
        return _uma(Cliente, self.db.execute("SELECT * FROM clientes WHERE email=? COLLATE NOCASE", (email,)).fetchone())

    def adicionar_favorito(self, cliente_id, livro_id):
        self.db.execute("INSERT OR IGNORE INTO favoritos VALUES (?,?)", (cliente_id, livro_id))

    def remover_favorito(self, cliente_id, livro_id):
        self.db.execute("DELETE FROM favoritos WHERE cliente_id=? AND livro_id=?", (cliente_id, livro_id))

    def favoritos(self, cliente_id):
        return _todas(Livro, self.db.execute("SELECT b.* FROM livros b JOIN favoritos f ON b.id=f.livro_id WHERE f.cliente_id=? ORDER BY b.id", (cliente_id,)))

    def notificar(self, cliente_id, tipo, mensagem):
        self.db.execute("INSERT INTO notificacoes(cliente_id,tipo,mensagem) VALUES (?,?,?)", (cliente_id, tipo, mensagem))

    def notificacoes(self, cliente_id):
        return _todas(Notificacao, self.db.execute("SELECT * FROM notificacoes WHERE cliente_id=? ORDER BY id DESC", (cliente_id,)))

    def registrar_alerta(self, cliente_id, edicao_id, loja_id):
        self.db.execute("INSERT OR IGNORE INTO alertas VALUES (?,?,?)", (cliente_id, edicao_id, loja_id))

    def consumir_alertas(self, edicao_id, loja_id):
        """Remove e devolve os IDs de clientes que aguardavam a reposição."""
        ids = [r[0] for r in self.db.execute("SELECT cliente_id FROM alertas WHERE edicao_id=? AND loja_id=? ORDER BY cliente_id", (edicao_id, loja_id))]
        self.db.execute("DELETE FROM alertas WHERE edicao_id=? AND loja_id=?", (edicao_id, loja_id))
        return ids


class PedidoRepositorio(_Repositorio):
    def criar_reserva(self, cliente_id, edicao_id, loja_id, preco_centavos):
        return self.db.execute("INSERT INTO reservas(cliente_id,edicao_id,loja_id,estado,preco_centavos) VALUES (?,?,?,'confirmada',?)", (cliente_id, edicao_id, loja_id, preco_centavos)).lastrowid

    def definir_codigo(self, reserva_id, codigo):
        self.db.execute("UPDATE reservas SET codigo=? WHERE id=?", (codigo, reserva_id))

    def obter_reserva(self, reserva_id):
        return _uma(Reserva, self.db.execute("SELECT * FROM reservas WHERE id=?", (reserva_id,)).fetchone())

    def reserva_do_cliente(self, cliente_id, codigo):
        return _uma(Reserva, self.db.execute("SELECT * FROM reservas WHERE codigo=? AND cliente_id=?", (codigo, cliente_id)).fetchone())

    def atualizar_estado(self, reserva):
        self.db.execute("UPDATE reservas SET estado=? WHERE id=?", (reserva.estado, reserva.id))

    def criar_compra(self, cliente_id, edicao_id, loja_id, preco_centavos, reserva_id=None):
        identificador = self.db.execute("INSERT INTO compras(cliente_id,edicao_id,loja_id,preco_centavos,reserva_id) VALUES (?,?,?,?,?)", (cliente_id, edicao_id, loja_id, preco_centavos, reserva_id)).lastrowid
        return _uma(Compra, self.db.execute("SELECT * FROM compras WHERE id=?", (identificador,)).fetchone())

    def reservas_do_cliente(self, cliente_id):
        return _todas(Reserva, self.db.execute("SELECT r.*, b.titulo, e.nome AS edicao, l.nome AS loja, s.secao FROM reservas r JOIN edicoes e ON e.id=r.edicao_id JOIN livros b ON b.id=e.livro_id JOIN lojas l ON l.id=r.loja_id JOIN estoques s ON s.edicao_id=r.edicao_id AND s.loja_id=r.loja_id WHERE r.cliente_id=? ORDER BY r.id DESC", (cliente_id,)))

    def compras_do_cliente(self, cliente_id):
        return _todas(Compra, self.db.execute("SELECT c.*, b.titulo, e.nome AS edicao, l.nome AS loja FROM compras c JOIN edicoes e ON e.id=c.edicao_id JOIN livros b ON b.id=e.livro_id JOIN lojas l ON l.id=c.loja_id WHERE c.cliente_id=? ORDER BY c.id DESC", (cliente_id,)))
