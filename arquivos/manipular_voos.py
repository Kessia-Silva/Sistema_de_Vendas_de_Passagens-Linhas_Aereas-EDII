import json
import os

ARQUIVO_VOOS = os.path.join("arquivos", "voos.json")

def carregar_voos():
    try:
        with open(ARQUIVO_VOOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Se o arquivo ainda não existir

def salvar_voos(voos):
    with open(ARQUIVO_VOOS, "w", encoding="utf-8") as f:
        json.dump(voos, f, indent=4, ensure_ascii=False)
