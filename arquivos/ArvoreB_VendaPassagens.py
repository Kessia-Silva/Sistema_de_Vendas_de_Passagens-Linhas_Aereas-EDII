from arquivos.manipular_VendasPassagens import carregar_registros_passagens
from arquivos.ArvoreB_classe import ArvoreB


class RegistroPassagem:
    def __init__(self, codigo_passagem, cpf, codigo_voo, assento):
        self.codigo_passagem = codigo_passagem
        self.cpf = cpf
        self.codigo_voo = codigo_voo
        self.assento = assento

    def __repr__(self):
        return (
            f"(Passagem: {self.codigo_passagem}, CPF: {self.cpf}, "
            f"Voo: {self.codigo_voo}, Assento: {self.assento})"
        )



# Criar a árvore
arvore = ArvoreB(ordem=4)

# Carregar dicionários do arquivo
lista_dicts = carregar_registros_passagens()

# Converter cada dicionário em objeto RegistroPassagem
for d in lista_dicts:
    registro = RegistroPassagem(
        d["codigo_passagem"],
        d["cpf"],
        d["codigo_voo"],
        d["assento"]
    )

    # Inserir na Árvore B
    arvore.inserir(registro)

def reconstruir_arvore():
    # 1. Criar a árvore vazia
    arvore = ArvoreB(ordem=4)

    # 2. Carregar dicionários do arquivo
    lista_dicts = carregar_registros_passagens()

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






