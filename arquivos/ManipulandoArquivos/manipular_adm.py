import json
import os

ARQUIVO_ADMS = os.path.join("arquivos", "adms.json")

def carregar_adms():
    try:
        with open(ARQUIVO_ADMS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Se o arquivo ainda não existir

def salvar_adms(adms):
    with open(ARQUIVO_ADMS, "w", encoding="utf-8") as f:
        json.dump(adms, f, indent=4, ensure_ascii=False)
