"""Ponto de entrada: sobe a camada de apresentação."""
from livraria.apresentacao import create_app

if __name__ == "__main__":
    create_app().run(debug=False)
