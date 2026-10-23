"""Regras de catálogo: busca sem acento/caixa e preço com promoção (R01, R02)."""
import unicodedata


def normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", str(texto)).casefold() if not unicodedata.combining(c))


def combina_busca(livro, titulo="", autor="", genero=""):
    """Todos os filtros preenchidos precisam aparecer no campo correspondente."""
    filtros = {"titulo": titulo, "autor": autor, "genero": genero}
    return all(normalizar(termo) in normalizar(livro[campo]) for campo, termo in filtros.items() if termo)


def preco_final(preco_centavos, promocoes):
    return max(0, preco_centavos - sum(p["desconto_centavos"] for p in promocoes))
