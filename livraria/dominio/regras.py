"""Regras de negócio puras (R01–R06)."""
import re
import unicodedata

from livraria.dominio.excecoes import RegraInvalida


def normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFKD", str(texto)).casefold()
                   if not unicodedata.combining(c))


def corresponde(livro, titulo="", autor="", genero=""):
    """R01: fragmentos sem caixa/acentos, combinados com E."""
    return all(normalizar(termo) in normalizar(getattr(livro, campo))
               for campo, termo in (("titulo", titulo), ("autor", autor), ("genero", genero)) if termo)


def preco_final(preco_centavos, promocoes):
    """R02: preço menos descontos ativos, nunca negativo."""
    return max(0, preco_centavos - sum(p.desconto_centavos for p in promocoes if p.ativa))


def lista_interesses(interesses):
    return [p.strip() for p in interesses.split(",") if p.strip()]


def validar_cadastro(nome, email, bairro, interesses=""):
    """R04: devolve os campos normalizados ou falha."""
    nome, email, bairro = nome.strip(), email.strip().lower(), bairro.strip()
    if not nome or not bairro or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise RegraInvalida("Informe nome, email válido e bairro.")
    return nome, email, bairro, ",".join(lista_interesses(interesses))


def tem_interesse(cliente, genero):
    return normalizar(genero) in [normalizar(x) for x in lista_interesses(cliente.interesses)]


def recomendar(cliente, livros, favoritos_ids):
    """R02: livros do gênero de interesse ainda não favoritados, em ordem de id."""
    return [b for b in sorted(livros, key=lambda b: b.id) if b.id not in favoritos_ids and tem_interesse(cliente, b.genero)]


def codigo_reserva(identificador):
    return f"RES-{identificador:06d}"


def pontos_fidelidade(compras):
    """R05: um ponto por real inteiro de cada compra concluída."""
    return sum(c.preco_centavos // 100 for c in compras)


TEXTO_AVALIACAO_MAX = 500


def validar_avaliacao(nota, texto=""):
    """R07: nota inteira 1..5 e texto opcional de até 500 caracteres."""
    try:
        nota = int(nota)
    except (TypeError, ValueError):
        raise RegraInvalida("A nota deve ser um número inteiro de 1 a 5.") from None
    texto = (texto or "").strip()
    if not 1 <= nota <= 5:
        raise RegraInvalida("A nota deve ser um número inteiro de 1 a 5.")
    if len(texto) > TEXTO_AVALIACAO_MAX:
        raise RegraInvalida(f"O texto da avaliação aceita até {TEXTO_AVALIACAO_MAX} caracteres.")
    return nota, texto


def media_avaliacoes(avaliacoes):
    """R07: média com uma casa decimal (None sem avaliações)."""
    return round(sum(a.nota for a in avaliacoes) / len(avaliacoes), 1) if avaliacoes else None


def exigir_esgotado(estoque):
    """R06: alerta só para edição esgotada na unidade."""
    if not estoque or estoque.quantidade != 0:
        raise RegraInvalida("Alerta permitido apenas para edição esgotada na unidade.")
