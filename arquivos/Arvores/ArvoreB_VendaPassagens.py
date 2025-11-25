from arquivos.ManipulandoArquivos.manipular_Reservas import carregar_reservas
from arquivos.Arvores.ArvoreB_Passagens_classe import ArvoreB
from arquivos.Classes.ClasseReserva import RegistroPassagem

def reconstruir_arvore():
    # Criar a árvore B vazia
    arvore = ArvoreB(ordem=4)

    # Carregar lista de dicionários
    lista_reservas = carregar_reservas()

    # Inserir chave + posição na árvore
    for posicao, registro in enumerate(lista_reservas):
        chave = registro["codigo_passagem"]
        arvore.inserir(chave, posicao)

    return arvore

def retornarInformacoesRegistro(arvore, chave):
    # 1. Busca posição na árvore B
    posicao = arvore.buscar(chave)
    if posicao is None:
        return None  # chave não encontrada

    # 2. Carrega todas as reservas do arquivo
    lista = carregar_reservas()

    if posicao < 0 or posicao >= len(lista):
        return None

    # 3. Pega registro correspondente no JSON
    dados = lista[posicao]

    # 4. Cria e retorna o objeto RegistroPassagem
    return RegistroPassagem(
        dados["codigo_passagem"],
        dados["cpf"],
        dados["codigo_voo"],
        dados["assento"],
        dados["preco"],
        dados["rota"]
    )

def inserirArvore(arvore, chave):
    # 1. Carregar lista do arquivo
    lista = carregar_reservas()

    # 2. Calcular posição pela própria ordem do arquivo
    posicao = next(
        (i for i, r in enumerate(lista) if r["codigo_passagem"] == chave),
        None
    )

    # 3. Se não achar, não insere
    if posicao is None:
        return False

    # 4. Inserir chave + posição na árvore B
    arvore.inserir(chave, posicao)
    return True



# Criar a árvore
arvore = reconstruir_arvore()
