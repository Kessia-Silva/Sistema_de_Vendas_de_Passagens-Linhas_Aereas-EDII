from arquivos.ManipulandoArquivos.manipularClientes import carregar_clientes
from arquivos.Arvores.ArvoreB_Clientes_classe import ArvoreBClientes
from arquivos.Classes.ClasseClientes import Cliente

def reconstruir_arvore_clientes():
    # 1. Criar árvore vazia
    arvore = ArvoreBClientes(ordem=4)

    # 2. Carregar lista bruta do arquivo
    lista_dicts = carregar_clientes()

    # 3. Inserir APENAS cpf + posição no arquivo
    for pos, d in enumerate(lista_dicts):
        cpf = d["cpf"]
        arvore.inserir(cpf, pos)

    return arvore

def retornarClientePorCPF(arvore_clientes, cpf):
    # 1. Buscar posição na Árvore B
    pos = arvore_clientes.buscar(cpf)
    if pos is None:
        return None  # cliente não existe

    # 2. Carregar lista completa do arquivo
    lista_dicts = carregar_clientes()

    # 3. Garantir que a posição existe
    if pos < 0 or pos >= len(lista_dicts):
        return None

    # 4. Construir o objeto Cliente
    d = lista_dicts[pos]
    cliente = Cliente(
        cpf=d["cpf"],
        nome=d["nome"],
        reservas=d.get("reservas"),
        datas=d.get("datas"),
        milhas=d.get("milhas")
    )

    return cliente


# Criar a árvore reconstruída
arvore_clientes = reconstruir_arvore_clientes()
