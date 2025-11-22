import json

def carregar_clientes():
    try:
        with open("arquivos/clientes.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def salvar_clientes(clientes):
    with open("arquivos/clientes.json", "w", encoding="utf-8") as f:
        json.dump(clientes, f, indent=4, ensure_ascii=False)

