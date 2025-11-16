import json
import os

ARQUIVO_REGISTRO = os.path.join("arquivos", "RegistroVendaPassagens.json")

def carregar_registros_passagens():
    try:
        with open(ARQUIVO_REGISTRO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Caso o arquivo ainda não exista

def salvar_registros_passagens(registros):
    with open(ARQUIVO_REGISTRO, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)
