"""Garante a direção das dependências entre camadas lendo os imports (ast)."""
import ast
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "livraria"

# camada -> prefixos de módulos que ela NÃO pode importar
PROIBIDOS = {
    "dominio": ("flask", "sqlite3", "livraria.dados", "livraria.aplicacao", "livraria.apresentacao"),
    "dados": ("flask", "livraria.aplicacao", "livraria.apresentacao"),
    "aplicacao": ("flask", "sqlite3", "livraria.apresentacao"),
    "apresentacao": ("sqlite3", "livraria.dados", "livraria.dominio"),
}


def importados(arquivo):
    pacote = ["livraria", *arquivo.relative_to(RAIZ).parent.parts]
    for no in ast.walk(ast.parse(arquivo.read_text(), str(arquivo))):
        if isinstance(no, ast.Import):
            yield from (a.name for a in no.names)
        elif isinstance(no, ast.ImportFrom):
            base = pacote[:len(pacote) - no.level + 1] if no.level else []
            yield ".".join(base + ([no.module] if no.module else []))


class ArquiteturaTest(unittest.TestCase):
    def test_camadas_respeitam_dependencias(self):
        for camada, proibidos in PROIBIDOS.items():
            arquivos = list((RAIZ / camada).rglob("*.py"))
            self.assertTrue(arquivos, camada)
            for arquivo in arquivos:
                for modulo in importados(arquivo):
                    with self.subTest(arquivo=arquivo.name, modulo=modulo):
                        self.assertFalse(any(modulo == p or modulo.startswith(p + ".") for p in proibidos),
                                         f"{camada}/{arquivo.name} não pode importar {modulo}")

    def test_leitor_de_imports_enxerga_as_dependencias_permitidas(self):
        self.assertIn("livraria.aplicacao", set(importados(RAIZ / "apresentacao" / "app.py")))
        self.assertIn("livraria.dados", set(importados(RAIZ / "aplicacao" / "servicos.py")))
        self.assertIn("livraria.dominio.entidades", set(importados(RAIZ / "dados" / "repositorios.py")))


if __name__ == "__main__":
    unittest.main()
