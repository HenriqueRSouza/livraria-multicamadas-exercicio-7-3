"""Camada de Dados: conexão com o SQLite, tabelas, dados de exemplo e todas as consultas SQL."""
import sqlite3
from contextlib import contextmanager

ESQUEMA = """
CREATE TABLE IF NOT EXISTS livros(id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, autor TEXT NOT NULL, genero TEXT NOT NULL, sinopse TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS edicoes(id INTEGER PRIMARY KEY, livro_id INTEGER NOT NULL REFERENCES livros, nome TEXT NOT NULL, ano INTEGER NOT NULL, preco_centavos INTEGER NOT NULL CHECK(preco_centavos>=0));
CREATE TABLE IF NOT EXISTS lojas(id INTEGER PRIMARY KEY, nome TEXT NOT NULL, bairro TEXT NOT NULL, endereco TEXT NOT NULL, horario TEXT NOT NULL, pagamentos TEXT NOT NULL, servicos TEXT NOT NULL, cafe INTEGER NOT NULL, eventos TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS estoques(edicao_id INTEGER NOT NULL REFERENCES edicoes, loja_id INTEGER NOT NULL REFERENCES lojas, quantidade INTEGER NOT NULL CHECK(quantidade>=0), secao TEXT NOT NULL, PRIMARY KEY(edicao_id,loja_id));
CREATE TABLE IF NOT EXISTS clientes(id INTEGER PRIMARY KEY, nome TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE, bairro TEXT NOT NULL, interesses TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS avaliacoes(id INTEGER PRIMARY KEY, livro_id INTEGER NOT NULL REFERENCES livros, cliente_id INTEGER REFERENCES clientes, nota INTEGER NOT NULL CHECK(nota BETWEEN 1 AND 5), texto TEXT NOT NULL CHECK(length(texto)<=500), autor TEXT NOT NULL, UNIQUE(cliente_id,livro_id));
CREATE TABLE IF NOT EXISTS promocoes(id INTEGER PRIMARY KEY, edicao_id INTEGER NOT NULL REFERENCES edicoes, descricao TEXT NOT NULL, desconto_centavos INTEGER NOT NULL CHECK(desconto_centavos>=0), ativa INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS favoritos(cliente_id INTEGER NOT NULL REFERENCES clientes, livro_id INTEGER NOT NULL REFERENCES livros, PRIMARY KEY(cliente_id,livro_id));
CREATE TABLE IF NOT EXISTS reservas(id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL REFERENCES clientes, edicao_id INTEGER NOT NULL REFERENCES edicoes, loja_id INTEGER NOT NULL REFERENCES lojas, codigo TEXT UNIQUE, estado TEXT NOT NULL CHECK(estado IN ('confirmada','retirada','cancelada')), preco_centavos INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS compras(id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL REFERENCES clientes, edicao_id INTEGER NOT NULL REFERENCES edicoes, loja_id INTEGER NOT NULL REFERENCES lojas, preco_centavos INTEGER NOT NULL, reserva_id INTEGER UNIQUE REFERENCES reservas);
CREATE TABLE IF NOT EXISTS alertas(cliente_id INTEGER NOT NULL REFERENCES clientes, edicao_id INTEGER NOT NULL REFERENCES edicoes, loja_id INTEGER NOT NULL REFERENCES lojas, PRIMARY KEY(cliente_id,edicao_id,loja_id));
CREATE TABLE IF NOT EXISTS notificacoes(id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL REFERENCES clientes, tipo TEXT NOT NULL, mensagem TEXT NOT NULL);
"""


def _dados_exemplo(db):
    db.executemany("INSERT INTO livros VALUES (?,?,?,?,?)", [
        (1, "A Casa das Marés", "L. Andrade", "Ficção", "Uma viagem às memórias de uma cidade costeira."),
        (2, "Python para Todos", "Ana Ribeiro", "Tecnologia", "Introdução prática à programação."),
    ])
    db.executemany("INSERT INTO edicoes VALUES (?,?,?,?,?)", [
        (1, 1, "Brochura", 2024, 5000), (2, 1, "Capa dura", 2025, 7500),
        (3, 2, "Brochura", 2024, 8000),
    ])
    db.executemany("INSERT INTO lojas VALUES (?,?,?,?,?,?,?,?,?)", [
        (1, "Unidade Centro", "Centro", "Rua das Flores, 10", "Seg–Sáb 9h–18h", "Pix, cartão (simulados)", "Retirada, acessibilidade", 1, "Clube do livro aos sábados"),
        (2, "Unidade Jardim", "Jardim", "Av. Verde, 22", "Seg–Sáb 10h–19h", "Pix, cartão (simulados)", "Retirada", 0, "Oficina de leitura mensal"),
    ])
    db.executemany("INSERT INTO estoques VALUES (?,?,?,?)", [
        (1, 1, 1, "Literatura"), (1, 2, 2, "Ficção"), (2, 1, 0, "Literatura"),
        (2, 2, 1, "Ficção"), (3, 1, 2, "Tecnologia"), (3, 2, 0, "Tecnologia"),
    ])
    db.execute("INSERT INTO avaliacoes(id,livro_id,nota,texto,autor) VALUES (1,1,5,'Envolvente','Leitora demo')")
    db.execute("INSERT INTO promocoes VALUES (1,1,'Oferta de demonstração',1000,1)")


class Banco:
    def __init__(self, caminho):
        self.caminho = str(caminho)
        with self.conexao() as con:
            con.executescript(ESQUEMA)
            if not con.execute("SELECT 1 FROM livros LIMIT 1").fetchone():
                _dados_exemplo(con)

    @contextmanager
    def conexao(self, transacao=False):
        """Abre uma conexão; com transacao=True trava a escrita (débito de estoque atômico)."""
        con = sqlite3.connect(self.caminho, timeout=10)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        try:
            if transacao:
                con.execute("BEGIN IMMEDIATE")
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()


def _lista(cursor):
    return [dict(r) for r in cursor]


def _um(cursor):
    row = cursor.fetchone()
    return dict(row) if row else None


# Catálogo
def livros(con):
    return _lista(con.execute("SELECT * FROM livros ORDER BY id"))


def livro(con, livro_id):
    return _um(con.execute("SELECT * FROM livros WHERE id=?", (livro_id,)))


def edicoes(con, livro_id):
    return _lista(con.execute("SELECT * FROM edicoes WHERE livro_id=? ORDER BY id", (livro_id,)))


def edicao(con, edicao_id):
    return _um(con.execute("SELECT * FROM edicoes WHERE id=?", (edicao_id,)))


def promocoes_ativas(con, edicao_id=None):
    if edicao_id is None:
        return _lista(con.execute("SELECT p.*, b.genero FROM promocoes p JOIN edicoes e ON e.id=p.edicao_id JOIN livros b ON b.id=e.livro_id WHERE p.ativa=1"))
    return _lista(con.execute("SELECT * FROM promocoes WHERE edicao_id=? AND ativa=1", (edicao_id,)))


def avaliacoes(con, livro_id):
    return _lista(con.execute("SELECT * FROM avaliacoes WHERE livro_id=? ORDER BY id", (livro_id,)))


def salvar_avaliacao(con, livro_id, cliente_id, nota, texto, autor):
    con.execute("INSERT INTO avaliacoes(livro_id,cliente_id,nota,texto,autor) VALUES (?,?,?,?,?) "
                "ON CONFLICT(cliente_id,livro_id) DO UPDATE SET nota=excluded.nota, texto=excluded.texto",
                (livro_id, cliente_id, nota, texto, autor))


def avaliacoes_do_cliente(con, cliente_id):
    return _lista(con.execute("SELECT a.*, b.titulo FROM avaliacoes a JOIN livros b ON b.id=a.livro_id WHERE a.cliente_id=? ORDER BY a.id DESC", (cliente_id,)))


# Lojas e estoque
def lojas(con):
    return _lista(con.execute("SELECT * FROM lojas ORDER BY id"))


def estoques_da_edicao(con, edicao_id):
    return _lista(con.execute("SELECT s.*, l.nome AS loja_nome FROM estoques s JOIN lojas l ON l.id=s.loja_id WHERE s.edicao_id=? ORDER BY s.loja_id", (edicao_id,)))


def estoque(con, edicao_id, loja_id):
    return _um(con.execute("SELECT s.*, b.titulo, l.nome AS loja_nome FROM estoques s JOIN edicoes e ON e.id=s.edicao_id "
                           "JOIN livros b ON b.id=e.livro_id JOIN lojas l ON l.id=s.loja_id WHERE s.edicao_id=? AND s.loja_id=?", (edicao_id, loja_id)))


def alterar_estoque(con, edicao_id, loja_id, quantidade):
    con.execute("UPDATE estoques SET quantidade=? WHERE edicao_id=? AND loja_id=?", (quantidade, edicao_id, loja_id))


# Clientes
def inserir_cliente(con, nome, email, bairro, interesses):
    """Devolve o id, ou None se o email já existe."""
    try:
        return con.execute("INSERT INTO clientes(nome,email,bairro,interesses) VALUES (?,?,?,?)", (nome, email, bairro, interesses)).lastrowid
    except sqlite3.IntegrityError:
        return None


def cliente(con, cliente_id):
    return _um(con.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,)))


def cliente_por_email(con, email):
    return _um(con.execute("SELECT * FROM clientes WHERE email=? COLLATE NOCASE", (email,)))


def adicionar_favorito(con, cliente_id, livro_id):
    con.execute("INSERT OR IGNORE INTO favoritos VALUES (?,?)", (cliente_id, livro_id))


def remover_favorito(con, cliente_id, livro_id):
    con.execute("DELETE FROM favoritos WHERE cliente_id=? AND livro_id=?", (cliente_id, livro_id))


def favoritos(con, cliente_id):
    return _lista(con.execute("SELECT b.* FROM livros b JOIN favoritos f ON b.id=f.livro_id WHERE f.cliente_id=? ORDER BY b.id", (cliente_id,)))


def notificar(con, cliente_id, tipo, mensagem):
    con.execute("INSERT INTO notificacoes(cliente_id,tipo,mensagem) VALUES (?,?,?)", (cliente_id, tipo, mensagem))


def notificacoes(con, cliente_id):
    return _lista(con.execute("SELECT * FROM notificacoes WHERE cliente_id=? ORDER BY id DESC", (cliente_id,)))


def adicionar_alerta(con, cliente_id, edicao_id, loja_id):
    con.execute("INSERT OR IGNORE INTO alertas VALUES (?,?,?)", (cliente_id, edicao_id, loja_id))


def consumir_alertas(con, edicao_id, loja_id):
    """Remove os alertas da edição/loja e devolve os ids dos clientes que pediram."""
    ids = [r["cliente_id"] for r in con.execute("SELECT cliente_id FROM alertas WHERE edicao_id=? AND loja_id=?", (edicao_id, loja_id))]
    con.execute("DELETE FROM alertas WHERE edicao_id=? AND loja_id=?", (edicao_id, loja_id))
    return ids


# Pedidos
def inserir_reserva(con, cliente_id, edicao_id, loja_id, preco):
    reserva_id = con.execute("INSERT INTO reservas(cliente_id,edicao_id,loja_id,estado,preco_centavos) VALUES (?,?,?,'confirmada',?)",
                             (cliente_id, edicao_id, loja_id, preco)).lastrowid
    con.execute("UPDATE reservas SET codigo=? WHERE id=?", (f"RES-{reserva_id:06d}", reserva_id))
    return _um(con.execute("SELECT * FROM reservas WHERE id=?", (reserva_id,)))


def reserva_por_codigo(con, codigo):
    return _um(con.execute("SELECT * FROM reservas WHERE codigo=?", (codigo,)))


def alterar_estado_reserva(con, reserva_id, estado):
    con.execute("UPDATE reservas SET estado=? WHERE id=?", (estado, reserva_id))


def inserir_compra(con, cliente_id, edicao_id, loja_id, preco, reserva_id=None):
    compra_id = con.execute("INSERT INTO compras(cliente_id,edicao_id,loja_id,preco_centavos,reserva_id) VALUES (?,?,?,?,?)",
                            (cliente_id, edicao_id, loja_id, preco, reserva_id)).lastrowid
    return _um(con.execute("SELECT * FROM compras WHERE id=?", (compra_id,)))


def reservas_do_cliente(con, cliente_id):
    return _lista(con.execute("SELECT r.*, b.titulo, e.nome AS edicao, l.nome AS loja, s.secao FROM reservas r JOIN edicoes e ON e.id=r.edicao_id "
                              "JOIN livros b ON b.id=e.livro_id JOIN lojas l ON l.id=r.loja_id JOIN estoques s ON s.edicao_id=r.edicao_id AND s.loja_id=r.loja_id "
                              "WHERE r.cliente_id=? ORDER BY r.id DESC", (cliente_id,)))


def compras_do_cliente(con, cliente_id):
    return _lista(con.execute("SELECT c.*, b.titulo, e.nome AS edicao, l.nome AS loja FROM compras c JOIN edicoes e ON e.id=c.edicao_id "
                              "JOIN livros b ON b.id=e.livro_id JOIN lojas l ON l.id=c.loja_id WHERE c.cliente_id=? ORDER BY c.id DESC", (cliente_id,)))
