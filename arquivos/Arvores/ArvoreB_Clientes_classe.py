# ========================================
# OBJETO DA CHAVE NA ÁRVORE
# ========================================
class ChaveCliente:
    def __init__(self, cpf, pos):
        self.cpf = cpf
        self.pos = pos


# ========================================
# CLASSE DO NÓ DA ÁRVORE B
# ========================================
class NoB:
    def __init__(self, eh_folha=True):
        self.chaves = []      # lista de objetos ChaveCliente
        self.filhos = []
        self.eh_folha = eh_folha


# ========================================
# ÁRVORE B PARA CLIENTES
# ========================================
class ArvoreBClientes:
    def __init__(self, ordem):
        self.raiz = NoB(eh_folha=True)
        self.ordem = ordem


    # ----------------------------------------
    # INSERÇÃO PRINCIPAL
    # ----------------------------------------
    def inserir(self, cpf, pos):
        chave = ChaveCliente(cpf, pos)
        no_raiz = self.raiz

        if len(no_raiz.chaves) == (2 * self.ordem) - 1:
            nova_raiz = NoB(eh_folha=False)
            nova_raiz.filhos.append(no_raiz)
            self.dividir_no(nova_raiz, 0)
            self.raiz = nova_raiz
            self.inserir_nao_cheio(nova_raiz, chave)
        else:
            self.inserir_nao_cheio(no_raiz, chave)


    # ----------------------------------------
    # INSERIR EM NÓ NÃO CHEIO
    # ----------------------------------------
    def inserir_nao_cheio(self, no, chave):
        i = len(no.chaves) - 1

        if no.eh_folha:
            no.chaves.append(None)

            while i >= 0 and chave.cpf < no.chaves[i].cpf:
                no.chaves[i + 1] = no.chaves[i]
                i -= 1

            no.chaves[i + 1] = chave

        else:
            while i >= 0 and chave.cpf < no.chaves[i].cpf:
                i -= 1
            i += 1

            if len(no.filhos[i].chaves) == (2 * self.ordem) - 1:
                self.dividir_no(no, i)

                if chave.cpf > no.chaves[i].cpf:
                    i += 1

            self.inserir_nao_cheio(no.filhos[i], chave)


    # ----------------------------------------
    # DIVIDIR NÓ
    # ----------------------------------------
    def dividir_no(self, no_pai, indice_filho):
        ordem = self.ordem
        no_cheio = no_pai.filhos[indice_filho]
        novo_no = NoB(eh_folha=no_cheio.eh_folha)

        chave_do_meio = no_cheio.chaves[ordem - 1]

        no_pai.chaves.insert(indice_filho, chave_do_meio)

        novo_no.chaves = no_cheio.chaves[ordem:]
        no_cheio.chaves = no_cheio.chaves[:ordem - 1]

        if not no_cheio.eh_folha:
            novo_no.filhos = no_cheio.filhos[ordem:]
            no_cheio.filhos = no_cheio.filhos[:ordem]

        no_pai.filhos.insert(indice_filho + 1, novo_no)


    # ----------------------------------------
    # BUSCAR CPF → retorna posição no arquivo
    # ----------------------------------------
    def buscar(self, cpf, no=None):
        if no is None:
            no = self.raiz

        i = 0
        while i < len(no.chaves) and cpf > no.chaves[i].cpf:
            i += 1

        if i < len(no.chaves) and cpf == no.chaves[i].cpf:
            return no.chaves[i].pos

        if no.eh_folha:
            return None

        return self.buscar(cpf, no.filhos[i])


    # ----------------------------------------
    # IMPRIMIR ÁRVORE
    # ----------------------------------------
    def imprimir(self, no=None, nivel=0):
        if no is None:
            no = self.raiz

        lista = [f"{c.cpf}(pos:{c.pos})" for c in no.chaves]
        print("   " * nivel + f"Nível {nivel}: {lista}")

        for filho in no.filhos:
            self.imprimir(filho, nivel + 1)
