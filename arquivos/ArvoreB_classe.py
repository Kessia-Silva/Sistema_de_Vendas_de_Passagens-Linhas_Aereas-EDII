# ========================================
# CLASSE DO NÓ DA ÁRVORE B
# ========================================
class NoB:
    def __init__(self, eh_folha=True):
        self.chaves = []      # guarda objetos RegistroPassagem
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
    # Inserção principal
    # ----------------------------------------
    def inserir(self, registro):
        no_raiz = self.raiz

        # Verifica se a raiz está cheia
        if len(no_raiz.chaves) == (2 * self.ordem) - 1:
            nova_raiz = NoB(eh_folha=False)
            nova_raiz.filhos.append(no_raiz)
            self.dividir_no(nova_raiz, 0)
            self.raiz = nova_raiz
            self.inserir_nao_cheio(self.raiz, registro)
        else:
            self.inserir_nao_cheio(no_raiz, registro)


    # ----------------------------------------
    # Inserir em nó NÃO cheio
    # ----------------------------------------
    def inserir_nao_cheio(self, no, registro):
        i = len(no.chaves) - 1

        # Caso 1: nó folha
        if no.eh_folha:

            no.chaves.append(None)

            # Desloca os elementos até achar a posição certa
            while (
                i >= 0 
                and registro.codigo_passagem < no.chaves[i].codigo_passagem
            ):
                no.chaves[i + 1] = no.chaves[i]
                i -= 1

            no.chaves[i + 1] = registro

        # Caso 2: nó interno
        else:
            while (
                i >= 0 
                and registro.codigo_passagem < no.chaves[i].codigo_passagem
            ):
                i -= 1
            i += 1

            # Se o filho escolhido estiver cheio → dividir
            if len(no.filhos[i].chaves) == (2 * self.ordem) - 1:
                self.dividir_no(no, i)
                
                # Decidir se vai para o filho da direita
                if registro.codigo_passagem > no.chaves[i].codigo_passagem:
                    i += 1

            self.inserir_nao_cheio(no.filhos[i], registro)


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
    # Impressão da árvore
    # ----------------------------------------
    def imprimir(self, no=None, nivel=0):
        if no is None:
            no = self.raiz
        
        # Para mostrar só o código das passagens
        lista_formatada = [obj.codigo_passagem for obj in no.chaves]
        print("   " * nivel + str(lista_formatada))

        for filho in no.filhos:
            self.imprimir(filho, nivel + 1)
    
    # ----------------------------------------
    # Impressão da árvore por nivel
    # ----------------------------------------

    def imprimirNivel(self, no=None, nivel=0):
      if no is None:
        no = self.raiz
    
      lista_formatada = [obj.codigo_passagem for obj in no.chaves]
    
       # Imprime o nível
      print(f"Nível {nivel}: {lista_formatada}")

      # Chama recursivamente para os filhos
      for filho in no.filhos:
        self.imprimir(filho, nivel + 1)

    # ----------------------------------------
    # Buscar na arvore
    # ----------------------------------------
    def buscar(self, codigo_passagem, no=None):
     if no is None:
        no = self.raiz

     i = 0
     # Procura a posição onde o código poderia estar
     while i < len(no.chaves) and codigo_passagem > no.chaves[i].codigo_passagem:
        i += 1

     # Se encontrou exatamente o código
     if i < len(no.chaves) and codigo_passagem == no.chaves[i].codigo_passagem:
        return no.chaves[i]

     # Se for nó folha e não achou → retorna None
     if no.eh_folha:
        return None

     # Se não for folha → desce para o filho correto
     return self.buscar(codigo_passagem, no.filhos[i])
    
    
    # ----------------------------------------
    # Listar as chaves 
    # ----------------------------------------   
    def listar_chaves(self, no=None, lista=None):
     if lista is None:
        lista = []
     if no is None:
        no = self.raiz

    # Percorre todos os nós em ordem
     i = 0
     while i < len(no.chaves):
        # Se não for folha → desce no filho antes da chave
        if not no.eh_folha:
            self.listar_chaves(no.filhos[i], lista)

        lista.append(no.chaves[i])  # adiciona o objeto RegistroPassagem
        i += 1

    # Último filho
     if not no.eh_folha:
        self.listar_chaves(no.filhos[i], lista)

     return lista

    
    

 
