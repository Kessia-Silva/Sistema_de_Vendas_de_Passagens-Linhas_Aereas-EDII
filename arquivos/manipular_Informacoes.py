import json
import os

CAMINHO_ARQUIVO = os.path.join("arquivos", "informacoes.json")

def carregar_valor():
    if os.path.exists(CAMINHO_ARQUIVO):
        with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return None  # se não existir, retorna None

def salvar_valor(valor):
    os.makedirs(os.path.dirname(CAMINHO_ARQUIVO), exist_ok=True)
    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(valor, arquivo, ensure_ascii=False)
