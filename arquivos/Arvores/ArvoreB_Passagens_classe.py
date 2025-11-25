# ========================================
# CLASSE: Entrada do índice (chave + posição)
# ========================================
class EntradaIndice:
    def __init__(self, chave, pos):
        self.chave = chave   # ex: código da passagem
        self.pos = pos       # posição no arquivo


# ========================================
# CLASSE DO NÓ DA ÁRVORE B
# ========================================
class NoB:
    def __init__(self, eh_folha=True):
        self.chaves = []      # agora guarda objetos EntradaIndice
        self.filhos = []
        self.eh_folha = eh_folha


# ========================================
# CLASSE PRINCIPAL DA ÁRVORE B
# ========================================
class ArvoreB:
    def __init__(self, ordem):
        self.raiz = NoB(eh_folha=True)
        self.ordem = ordem


    # ----------------------------------------
    # INSERÇÃO PRINCIPAL
    # ----------------------------------------
    def inserir(self, chave, pos):
        entrada = EntradaIndice(chave, pos)
        no_raiz = self.raiz

        if len(no_raiz.chaves) == (2 * self.ordem) - 1:
            nova_raiz = NoB(eh_folha=False)
            nova_raiz.filhos.append(no_raiz)
            self.dividir_no(nova_raiz, 0)
            self.raiz = nova_raiz
            self.inserir_nao_cheio(self.raiz, entrada)
        else:
            self.inserir_nao_cheio(no_raiz, entrada)


    # ----------------------------------------
    # INSERIR EM NÓ NÃO CHEIO
    # ----------------------------------------
    def inserir_nao_cheio(self, no, entrada):
        i = len(no.chaves) - 1

        # Caso 1: Nó folha
        if no.eh_folha:
            no.chaves.append(None)

            while i >= 0 and entrada.chave < no.chaves[i].chave:
                no.chaves[i + 1] = no.chaves[i]
                i -= 1

            no.chaves[i + 1] = entrada

        # Caso 2: Nó interno
        else:
            while i >= 0 and entrada.chave < no.chaves[i].chave:
                i -= 1
            i += 1

            if len(no.filhos[i].chaves) == (2 * self.ordem) - 1:
                self.dividir_no(no, i)

                if entrada.chave > no.chaves[i].chave:
                    i += 1

            self.inserir_nao_cheio(no.filhos[i], entrada)


    # ----------------------------------------
    # DIVIDIR UM NÓ CHEIO
    # ----------------------------------------
    def dividir_no(self, no_pai, indice_filho):
        ordem = self.ordem
        no_cheio = no_pai.filhos[indice_filho]
        novo_no = NoB(eh_folha=no_cheio.eh_folha)

        # chave do meio sobe
        chave_do_meio = no_cheio.chaves[ordem - 1]
        no_pai.chaves.insert(indice_filho, chave_do_meio)

        # dividir chaves
        novo_no.chaves = no_cheio.chaves[ordem:]
        no_cheio.chaves = no_cheio.chaves[:ordem - 1]

        # dividir filhos (se não for folha)
        if not no_cheio.eh_folha:
            novo_no.filhos = no_cheio.filhos[ordem:]
            no_cheio.filhos = no_cheio.filhos[:ordem]

        no_pai.filhos.insert(indice_filho + 1, novo_no)


    # ----------------------------------------
    # BUSCAR – retorna posição no arquivo
    # ----------------------------------------
    def buscar(self, chave, no=None):
        if no is None:
            no = self.raiz

        i = 0
        while i < len(no.chaves) and chave > no.chaves[i].chave:
            i += 1

        if i < len(no.chaves) and chave == no.chaves[i].chave:
            return no.chaves[i].pos   # <-- retorno correto

        if no.eh_folha:
            return None

        return self.buscar(chave, no.filhos[i])


    # ----------------------------------------
    # IMPRIMIR
    # ----------------------------------------
    def imprimir(self, no=None, nivel=0):
        if no is None:
            no = self.raiz

        lista_formatada = [(e.chave, e.pos) for e in no.chaves]
        print("   " * nivel + str(lista_formatada))

        for filho in no.filhos:
            self.imprimir(filho, nivel + 1)


    # ----------------------------------------
    # LISTAR TODAS AS ENTRADAS EM ORDEM
    # ----------------------------------------
    def listar_chaves(self, no=None, lista=None):
        if lista is None:
            lista = []
        if no is None:
            no = self.raiz

        i = 0
        while i < len(no.chaves):
            if not no.eh_folha:
                self.listar_chaves(no.filhos[i], lista)

            lista.append(no.chaves[i])   # EntradaIndice
            i += 1

        if not no.eh_folha:
            self.listar_chaves(no.filhos[i], lista)

        return lista
