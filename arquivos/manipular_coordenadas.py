import json
import os

ARQUIVO_COORDENADAS = os.path.join("arquivos", "coordenadas_aeroportos.json")

def carregar_coordenadas():
    try:
        with open(ARQUIVO_COORDENADAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Se ainda não existir

def salvar_coordenadas(coordenadas):
    with open(ARQUIVO_COORDENADAS, "w", encoding="utf-8") as f:
        json.dump(coordenadas, f, indent=4, ensure_ascii=False)