import json
import os

CAMINHO_ARQUIVO = os.path.join("arquivos", "usuarios.json")

def carregar_usuarios():
    if os.path.exists(CAMINHO_ARQUIVO):
        with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return []  # se não existir, retorna lista vazia

def salvar_usuarios(lista):
    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(lista, arquivo, indent=4, ensure_ascii=False)
