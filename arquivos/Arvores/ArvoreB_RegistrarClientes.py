from arquivos.ManipulandoArquivos.manipularClientes import carregar_clientes
from arquivos.Arvores.ArvoreB_Clientes_classe import ArvoreBClientes
from arquivos.Classes.ClasseClientes import Cliente

def reconstruir_arvore_clientes():
    # 1. Criar a árvore vazia
    arvore = ArvoreBClientes(ordem=4)

    # 2. Carregar lista de clientes do arquivo
    lista_dicts = carregar_clientes()

    # 3. Converter cada dicionário em objeto Cliente e inserir na árvore
    for d in lista_dicts:
        cliente = Cliente(
            cpf=d["cpf"],
            nome=d["nome"],
            reservas=d.get("reservas", []),
            datas=d.get("datas", []),
            milhas=d.get("milhas", 0)
        )
        arvore.inserir(cliente)

    return arvore

# Criar a árvore
arvore_clientes = reconstruir_arvore_clientes()
