import json
import os

CAMINHO_RESERVAS = os.path.join("arquivos", "RegistroVendaPassagens.json")

def carregar_reservas():
    if os.path.exists(CAMINHO_RESERVAS):
        with open(CAMINHO_RESERVAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_reservas(reservas):
    os.makedirs(os.path.dirname(CAMINHO_RESERVAS), exist_ok=True)
    with open(CAMINHO_RESERVAS, "w", encoding="utf-8") as f:
        json.dump(reservas, f, indent=4, ensure_ascii=False)

def remover_reserva_do_arquivo(codigo_passagem):
    lista = carregar_reservas()
    lista = [r for r in lista if r["codigo_passagem"] != codigo_passagem]
    salvar_reservas(lista)
