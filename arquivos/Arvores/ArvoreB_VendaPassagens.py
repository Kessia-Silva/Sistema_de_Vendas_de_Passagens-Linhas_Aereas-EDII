from arquivos.ManipulandoArquivos.manipular_Reservas import carregar_reservas
from arquivos.Arvores.ArvoreB_Passagens_classe import ArvoreB
from arquivos.Classes.ClasseReserva import RegistroPassagem

def reconstruir_arvore():
    # 1. Criar a árvore vazia
    arvore = ArvoreB(ordem=4)

    # 2. Carregar dicionários do arquivo
    lista_dicts = carregar_reservas()

    # 3. Converter cada dicionário em objeto e inserir na árvore
    for d in lista_dicts:
        registro = RegistroPassagem(
            d["codigo_passagem"],
            d["cpf"],
            d["codigo_voo"],
            d["assento"]
        )
        arvore.inserir(registro)

    return arvore

# Criar a árvore
arvore = reconstruir_arvore()





