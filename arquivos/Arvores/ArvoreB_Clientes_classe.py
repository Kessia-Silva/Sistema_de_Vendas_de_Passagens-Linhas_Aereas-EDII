# ========================================
# CLASSE DO NÓ DA ÁRVORE B
# ========================================
class NoB:
    def __init__(self, eh_folha=True):
        self.chaves = []      # guarda objetos Cliente
        self.filhos = []
        self.eh_folha = eh_folha


# ========================================
# CLASSE PRINCIPAL DA ÁRVORE B
# ========================================
class ArvoreBClientes:
    def __init__(self, ordem):
        self.raiz = NoB(eh_folha=True)
        self.ordem = ordem


    # ----------------------------------------
    # Inserção principal
    # ----------------------------------------
    def inserir(self, cliente):
        no_raiz = self.raiz

        # Verifica se a raiz está cheia
        if len(no_raiz.chaves) == (2 * self.ordem) - 1:
            nova_raiz = NoB(eh_folha=False)
            nova_raiz.filhos.append(no_raiz)
            self.dividir_no(nova_raiz, 0)
            self.raiz = nova_raiz
            self.inserir_nao_cheio(self.raiz, cliente)
        else:
            self.inserir_nao_cheio(no_raiz, cliente)


    # ----------------------------------------
    # Inserir em nó NÃO cheio
    # ----------------------------------------
    def inserir_nao_cheio(self, no, cliente):
        i = len(no.chaves) - 1

        # Caso 1: nó folha
        if no.eh_folha:
            no.chaves.append(None)

            # Desloca os elementos até achar a posição certa
            while i >= 0 and cliente.cpf < no.chaves[i].cpf:
                no.chaves[i + 1] = no.chaves[i]
                i -= 1

            no.chaves[i + 1] = cliente

        # Caso 2: nó interno
        else:
            while i >= 0 and cliente.cpf < no.chaves[i].cpf:
                i -= 1
            i += 1

            # Se o filho escolhido estiver cheio → dividir
            if len(no.filhos[i].chaves) == (2 * self.ordem) - 1:
                self.dividir_no(no, i)
                
                # Decidir se vai para o filho da direita
                if cliente.cpf > no.chaves[i].cpf:
                    i += 1

            self.inserir_nao_cheio(no.filhos[i], cliente)


    # ----------------------------------------
    # Dividir um nó cheio
    # ----------------------------------------
    def dividir_no(self, no_pai, indice_filho):
        ordem = self.ordem
        no_cheio = no_pai.filhos[indice_filho]
        novo_no = NoB(eh_folha=no_cheio.eh_folha)

        # Chave do meio sobe
        chave_do_meio = no_cheio.chaves[ordem - 1]

        no_pai.chaves.insert(indice_filho, chave_do_meio)

        # Divide as chaves
        novo_no.chaves = no_cheio.chaves[ordem:]
        no_cheio.chaves = no_cheio.chaves[:ordem - 1]

        # Divide os filhos (se não for folha)
        if not no_cheio.eh_folha:
            novo_no.filhos = no_cheio.filhos[ordem:]
            no_cheio.filhos = no_cheio.filhos[:ordem]

        # Liga o novo nó ao pai
        no_pai.filhos.insert(indice_filho + 1, novo_no)


    # ----------------------------------------
    # Buscar cliente por CPF
    # ----------------------------------------
    def buscar(self, cpf, no=None):
        if no is None:
            no = self.raiz

        i = 0
        while i < len(no.chaves) and cpf > no.chaves[i].cpf:
            i += 1

        if i < len(no.chaves) and cpf == no.chaves[i].cpf:
            return no.chaves[i]

        if no.eh_folha:
            return None

        return self.buscar(cpf, no.filhos[i])


    # ----------------------------------------
    # Listar todos os clientes em ordem de CPF
    # ----------------------------------------
    def listar_chaves(self, no=None, lista=None):
        if lista is None:
            lista = []
        if no is None:
            no = self.raiz

        for i in range(len(no.chaves)):
            if not no.eh_folha:
                self.listar_chaves(no.filhos[i], lista)
            lista.append(no.chaves[i])

        if not no.eh_folha:
            self.listar_chaves(no.filhos[len(no.chaves)], lista)

        return lista


    # ----------------------------------------
    # Listar clientes por inicial do nome
    # ----------------------------------------
    def listar_por_inicial(self, letra, no=None, resultado=None):
        if resultado is None:
            resultado = []
        if no is None:
            no = self.raiz

        for i in range(len(no.chaves)):
            if not no.eh_folha:
                self.listar_por_inicial(letra, no.filhos[i], resultado)
            if no.chaves[i].nome.startswith(letra):
                resultado.append(no.chaves[i])

        if not no.eh_folha:
            self.listar_por_inicial(letra, no.filhos[len(no.chaves)], resultado)

        return resultado

    # ----------------------------------------
    # Imprimir a árvore completa por nível
    # ----------------------------------------
    def imprimir(self, no=None, nivel=0):
        if no is None:
            no = self.raiz

        # Mostra os CPFs e nomes dos clientes do nó atual
        lista_formatada = [f"{c.cpf} ({c.nome})" for c in no.chaves]
        print("   " * nivel + f"Nível {nivel}: {lista_formatada}")

        # Chama recursivamente para os filhos
        for filho in no.filhos:
            self.imprimir(filho, nivel + 1)
