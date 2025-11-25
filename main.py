from flask import Flask, render_template, request, redirect, url_for, jsonify, session #importando a classe Flask do pacote Flask
from arquivos.ManipulandoArquivos.manipular_usuarios import carregar_usuarios, salvar_usuarios # chamando o arquivo de usuarios
from arquivos.ManipulandoArquivos.manipular_voos import carregar_voos, salvar_voos # chamando as funções para manipular o arquivo de voos
from arquivos.ManipulandoArquivos.manipular_adm import carregar_adms #  chamando as funções para manipular o arquivo de adms
from arquivos.Arvores.ArvoreB_VendaPassagens import arvore, reconstruir_arvore, retornarInformacoesRegistro, inserirArvore#  chamando as funções para manipular Arvore de passagens
from arquivos.ManipulandoArquivos.manipular_Informacoes import carregar_valor, salvar_valor #  chamando as funções para manipular que salvar o codigo de passagens
from arquivos.ManipulandoArquivos.manipular_Reservas import carregar_reservas, salvar_reservas, remover_reserva_do_arquivo #  chamando as funções para manipular o arquivo de reservas 
from arquivos.Classes.ClasseReserva import RegistroPassagem # Importando classe de Reserva
from arquivos.respostas import respostas # Importando o arquivo de respostas do ChatBot
from arquivos.Arvores.ArvoreB_RegistrarClientes import arvore_clientes, reconstruir_arvore_clientes #  chamando as funções para manipular Arvore de clientes
from arquivos.ManipulandoArquivos.manipularClientes import salvar_clientes #  chamando as funções para manipular o arquivo de clientes
from arquivos.ManipulandoArquivos.manipular_coordenadas import carregar_coordenadas

import os
from igraph import Graph, plot
import folium

coordenadas_aeroportos = carregar_coordenadas()

app = Flask(__name__)  # cria a aplicação


app.secret_key = "123456"

# Variaveis globais
voos = carregar_voos()
adms = carregar_adms()
usuarios = carregar_usuarios()
reservas = carregar_reservas()
valor = carregar_valor()


# Definindo Rotas
#-----------Rotas principal ----------
@app.route("/")
def home():
    return render_template("home.html")

#-----------Rotas para Reservar um Voo ----------
@app.route("/reservar_voo")   
def reserva():
    return render_template("reservar_voo.html", voos_agendados = voos)

@app.route("/mapa_voo/<codigo>")
def mapaVoo(codigo):
    voo = next((v for v in voos if v["Codigo_do_voo"] == codigo), None)
    if voo is None:
        return "Voo não encontrado", 404

    total = voo["Numero_de_assentos"]
    ocupados = voo["Assentos_ocupados"]

    assentos = [
        {"numero": i, "status": "ocupado" if str(i) in ocupados else "livre"}
        for i in range(1, total + 1)
    ]

    return render_template("mapa_voo.html", voo=voo, assentos=assentos)

@app.route("/confirmarReserva/<codigo>/<assento>")
def confirmarReserva(codigo, assento):
    voo = next((v for v in voos if v["Codigo_do_voo"] == codigo), None)
    if voo is None:
        return "Voo não encontrado", 404

    return render_template("confirmarReserva.html", voo=voo, assento=assento, rota=session.get("rota"),
    preco=session.get("preco"))

# >>>>>>>>>>>>>>>>>> v v Manutenção v v <<<<<<<<<<<<<<<<<<<<
@app.route("/reservar_assento/<codigo>/<int:assento>", methods=["POST"])
def reservar_assento(codigo, assento):
    global valor
    cpf = session.get("cpf")

    # --- Reconstruir árvores sempre no começo ---
    arvore_clientes = reconstruir_arvore_clientes()
    arvore_passagens = reconstruir_arvore()

    cliente = arvore_clientes.buscar(cpf)
    if cliente is None:
        return "Cliente não encontrado", 404

    voo = next((v for v in voos if str(v["Codigo_do_voo"]) == codigo), None)
    if voo is None:
        return "Voo não encontrado", 404

    # Se o assento estiver livre
    if str(assento) not in voo["Assentos_ocupados"]:

        # 1. Marcar assento como ocupado
        voo["Assentos_ocupados"].append(str(assento))
        salvar_voos(voos)

        # 2. Criar nova reserva
        valor += 1
        salvar_valor(valor)

        registro = RegistroPassagem(
            codigo_passagem=valor,
            cpf=cpf,
            codigo_voo=codigo,
            assento=str(assento),
            preco=session.get("preco"),
            rota=session.get("rota")
        )

        # 3. Salvar reserva no arquivo JSON
        reservas.append({
            "codigo_passagem": registro.codigo_passagem,
            "cpf": registro.cpf,
            "codigo_voo": registro.codigo_voo,
            "assento": registro.assento,
            "preco": registro.preco,
            "rota": registro.rota
        })
        salvar_reservas(reservas)

        # 4. Inserir na árvore B (a posição será calculada automaticamente)
        inserirArvore(arvore_passagens, registro.codigo_passagem)

        # 5. Atualizar cliente (memória temporária)
        cliente.reservas.append(registro.codigo_passagem)
        cliente.datas.append(voo["Data"])

        # 6. Recalcular milhas
        total_milhas = 0
        arvore_passagens = reconstruir_arvore()  # Árvore atualizada após o insert

        for cod in cliente.reservas:
            reserva_temp = retornarInformacoesRegistro(arvore_passagens, cod)
            if reserva_temp:
                voo_temp = next((v for v in voos 
                    if str(v["Codigo_do_voo"]) == reserva_temp.codigo_voo), None)

                if voo_temp:
                    total_milhas += voo_temp["Milhas_percorridas"]

        cliente.milhas = total_milhas
        session['milhas'] = total_milhas

        # 7. Salvar todos os clientes
        clientes_dicts = clientes_para_dict(arvore_clientes.listar_chaves())
        salvar_clientes(clientes_dicts)

        # 8. Reconstruir novamente a árvore de clientes
        arvore_clientes = reconstruir_arvore_clientes()

    return "", 204



#-----------Rotas para Cancelar/Ve os Voos reservados ----------
    # >>>>>>>>>>>>>>>>>>>>>>>>> v v - Manutenção - v v <<<<<<<<<<<<<<<<<<<< !
@app.route("/minhas_reservas")
def minhas_reservas():
    cpf = session.get("cpf")
    if not cpf:
        return redirect(url_for("login_user"))

    # Reconstruir as árvores
    arvore_clientes = reconstruir_arvore_clientes()
    arvore_passagens = reconstruir_arvore()

    # Buscar cliente
    cliente = arvore_clientes.buscar(cpf)
    if not cliente:
        return redirect(url_for("login_user"))

    reservas_usuarios = []
    voos_encontrados = []

    # Para cada código de passagem do cliente
    for codigo_passagem in cliente.reservas:

        # Agora passando a árvore !
        reserva = retornarInformacoesRegistro(arvore_passagens, codigo_passagem)

        if reserva:
            reservas_usuarios.append(reserva)

            # Recuperar voo correspondente
            voo = next(
                (v for v in voos if str(v["Codigo_do_voo"]) == reserva.codigo_voo),
                None
            )
            if voo:
                voos_encontrados.append(voo)

    return render_template(
        "minhas_reservas.html",
        reservas_usuario=reservas_usuarios,
        voos_encontrados=voos_encontrados,
        cliente=cliente
    )


def clientes_para_dict(clientes_objetos):
    lista_dicts = []
    for c in clientes_objetos:
        lista_dicts.append({
            "cpf": c.cpf,
            "nome": c.nome,
            "reservas": c.reservas,
            "datas": c.datas,
            "milhas": c.milhas
        })
    return lista_dicts

# >>>>>>>>>>>>>>>>>> v v Manutenção v v <<<<<<<<<<<<<<<<<<<<
@app.route("/cancelar_reserva/<int:codigo_passagem>")
def cancelar_reserva(codigo_passagem):
    cpf = session.get("cpf")
    if not cpf:
        return redirect(url_for("login_user"))

    arvore_clientes = reconstruir_arvore_clientes()
    arvore_passagens = reconstruir_arvore()

    # 1. Ler reserva antes de mexer no arquivo
    reserva = retornarInformacoesRegistro(arvore_passagens, codigo_passagem)
    if not reserva:
        return redirect(url_for("minhas_reservas"))

    # 2. Liberar assento
    voo = next((v for v in voos if str(v["Codigo_do_voo"]) == reserva.codigo_voo), None)
    if voo and reserva.assento in voo["Assentos_ocupados"]:
        voo["Assentos_ocupados"].remove(reserva.assento)
    salvar_voos(voos)

    # 3. Remover do cliente
    cliente = arvore_clientes.buscar(cpf)
    if cliente and codigo_passagem in cliente.reservas:
        i = cliente.reservas.index(codigo_passagem)
        cliente.reservas.pop(i)
        cliente.datas.pop(i)

    # 4. Remover do arquivo AGORA
    remover_reserva_do_arquivo(codigo_passagem)

    # 5. RECONSTRUIR ÁRVORE AGORA pois o arquivo mudou
    arvore_passagens = reconstruir_arvore()

    # 6. Recalcular milhas
    total = 0
    for cod in cliente.reservas:
        r = retornarInformacoesRegistro(arvore_passagens, cod)
        if r:
            voo_temp = next((v for v in voos if str(v["Codigo_do_voo"]) == r.codigo_voo), None)
            if voo_temp:
                total += voo_temp["Milhas_percorridas"]

    cliente.milhas = total
    session["milhas"] = total

    # 7. Salvar clientes
    clientes_dicts = clientes_para_dict(arvore_clientes.listar_chaves())
    salvar_clientes(clientes_dicts)

    return redirect(url_for("minhas_reservas"))





#-----------Rotas para Telas iniciais do sistema ----------
@app.route("/InicialAdm")   
def editar():
    if "email" not in session:
        return redirect(url_for("login_adm"))  # bloqueia acesso direto
    return render_template("InicialAdm.html", voos_agendados = voos, email=session["email"])

# >>>>>>>>>>>>>>>>>> Manutenção <<<<<<<<<<<<<<<<<<<<
@app.route("/login_user", methods=["GET", "POST"])
def login_user():
    mensagem = ""  # só processa se o form for enviado
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Verifica email e senha
        for usuario in usuarios:
            if usuario["email"] == email and usuario["senha"] == senha:
                # Buscar o cliente na árvore
                cliente = arvore_clientes.buscar(usuario["cpf"])  # usando a árvore de clientes
                if cliente:
                    session["cpf"] = cliente.cpf  # guarda o cpf do cliente na sessão
                    session["email"] = usuario["email"]
                    return redirect(url_for("homeUser"))

        mensagem = "Email ou senha incorretos!"

    return render_template("login_user.html", mensagem=mensagem)

# >>>>>>>>>>>>>>>>>> Manutenção <<<<<<<<<<<<<<<<<<<<
@app.route("/homeUser")
def homeUser():
    cpf = session.get("cpf")
    if not cpf:
        return redirect(url_for("login_user"))
    
    arvore_clientes = reconstruir_arvore_clientes()
    cliente = arvore_clientes.buscar(cpf)
    email = session.get("email")
    return render_template("homeUser.html", cliente=cliente, email=email)


@app.route("/login_adm", methods = ["GET", "POST"])
def login_adm():
    mensagem = "" # só processa se o form for enviado 
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Verifica email e senha
        for adm in adms:
            if adm["email"] == email and adm["senha"] == senha:
                session["email"] = email  # guarda na sessão 
                return redirect(url_for("editar"))
            
            # Se o loop terminou e não retornou, então está errado
        mensagem = "Email ou senha incorretos!"

    return render_template("login_adm.html", mensagem=mensagem)

@app.route("/logoutAdm")
def logoutAdm():
    session.clear()
    return redirect(url_for("login_adm"))


@app.route("/logoutUser")
def logoutUser():
    session.clear()
    return redirect(url_for("login_user"))

#-----------Rotas para Funções de Adm ----------
@app.route("/criar_voo", methods=["GET", "POST"])
def criar_voo():
    mensagem = ""
    
    if request.method == "POST":
        codigo = request.form.get("Codigo_do_voo")
        origem = request.form.get("Origem")
        destino = request.form.get("Destino")
        preco = request.form.get("Preco_da_passagem")
        tipo_aeronave = request.form.get("Tipo_de_aeronave")
        assentos = request.form.get("Numero_de_assentos")
        hora = request.form.get("Hora")
        data = request.form.get("Data")
        milhas = request.form["Milhas_percorridas"]

        # Verifica se o código do voo já existe
        for voo in voos:
            if voo["Codigo_do_voo"] == codigo:
                mensagem = "Já existe um voo com esse código!"
                return render_template("criar_voo.html", mensagem=mensagem)

        # Adiciona o novo voo
        novo_voo = {
            "Codigo_do_voo": codigo,
            "Origem": origem,
            "Destino": destino,
            "Preco_da_passagem": float(preco),
            "Tipo_de_aeronave": tipo_aeronave,
            "Numero_de_assentos": int(assentos),
            "Hora": hora,
            "Data": data,
            "Assentos_ocupados": [],
            "Milhas_percorridas": int(milhas)
        }
        voos.append(novo_voo)
        salvar_voos(voos)
        mensagem = "Voo cadastrado com sucesso!"
        
        # redireciona para o site de criação de novo
        return render_template("criar_voo.html", mensagem=mensagem)

    return render_template("criar_voo.html", mensagem=mensagem)

@app.route("/editar_voo", methods=["GET", "POST"])
def editar_voo():
    mensagem = ""
    voo_selecionado = None

    # Se escolheu um voo para editar
    if request.method == "POST":
        codigo_escolhido = request.form.get("codigo_escolhido")

        # Se ele clicou em "Carregar voo"
        if "carregar" in request.form:
            for voo in voos:
                if voo["Codigo_do_voo"] == codigo_escolhido:
                    voo_selecionado = voo
                    break
            if not voo_selecionado:
                mensagem = "Voo não encontrado!"

        # Se ele clicou em "Salvar alterações"
        elif "salvar" in request.form:
            for voo in voos:
                if voo["Codigo_do_voo"] == codigo_escolhido:
                    voo["Origem"] = request.form.get("origem")
                    voo["Destino"] = request.form.get("destino")
                    voo["Preco_da_passagem"] = float(request.form.get("preco"))
                    voo["Tipo_de_aeronave"] = request.form.get("companhia")
                    voo["Numero_de_assentos"] = int(request.form.get("assentos"))
                    voo["Hora"] = request.form.get("hora")
                    voo["Data"] = request.form.get("dataPartida")
                    mensagem = "Voo atualizado com sucesso!"
                    voo_selecionado = voo
                    salvar_voos(voos)
                    break

    
    return render_template("editar_voo.html", voos=voos, voo=voo_selecionado, mensagem=mensagem)

@app.route("/remover_voo", methods=["GET", "POST"])
def remover_voo():
    global voos 

    voo = None
    mensagem = None

    if request.method == "POST":
        codigo = request.form.get("codigo_escolhido")

        # Quando clicar em "Carregar voo"
        if "carregar" in request.form:
            voo = next((v for v in voos if v["Codigo_do_voo"] == codigo), None)
            if not voo:
                mensagem = "Voo não encontrado."

        # Quando clicar em "Deletar Voo"
        elif "deletar" in request.form:
            voos = [v for v in voos if v["Codigo_do_voo"] != codigo]
            mensagem = f"Voo {codigo} removido com sucesso!"
            salvar_voos(voos)
            

    return render_template("remover_voo.html", voos=voos, voo=voo, mensagem=mensagem)

@app.route("/listar_voos")
def listar_voos():
    return render_template("listar_voos.html", voos=voos)


@app.route("/gerenciar_usuario", methods=["GET", "POST"])
def gerenciar_usuario():
    mensagem = ""
    usuario_selecionado = None

    if request.method == "POST":
        email_escolhido = request.form.get("email_escolhido", "").strip()

        if not email_escolhido:
            mensagem = "Por favor, selecione um usuário."
        else:
            # --- Carregar usuário ---
            if "carregar" in request.form:
                usuario_selecionado = next((u for u in usuarios if u["email"] == email_escolhido), None)
                if not usuario_selecionado:
                    mensagem = f"Usuário com e-mail {email_escolhido} não encontrado!"

            # --- Salvar alterações ---
            elif "salvar" in request.form:
                # Procura o índice do usuário na lista
                for i, u in enumerate(usuarios):
                    if u["email"] == email_escolhido:
                        # Atualiza os dados diretamente na lista
                        usuarios[i]["email"] = request.form.get("email", u["email"]).strip()
                        usuarios[i]["senha"] = request.form.get("senha", u["senha"]).strip()

                        # Atualiza objeto selecionado para o template
                        usuario_selecionado = usuarios[i]

                        # Salva no arquivo ou banco
                        salvar_usuarios(usuarios)
                        mensagem = f"Usuário {email_escolhido} atualizado com sucesso!"
                        break
                else:
                    mensagem = f"Usuário com e-mail {email_escolhido} não encontrado!"

            # --- Remover usuário ---
            elif "remover" in request.form:
                if any(u["email"] == email_escolhido for u in usuarios):
                    usuarios[:] = [u for u in usuarios if u["email"] != email_escolhido]
                    salvar_usuarios(usuarios)
                    mensagem = f"Usuário {email_escolhido} removido com sucesso!"
                    usuario_selecionado = None
                else:
                    mensagem = f"Usuário com e-mail {email_escolhido} não encontrado!"


            # --- Botão: Remover usuário ---
            elif "remover" in request.form:
                usuarios[:] = [u for u in usuarios if u["email"] != email_escolhido]
                salvar_usuarios(usuarios)
                mensagem = f"Usuário {email_escolhido} removido com sucesso!"
                usuario_selecionado = None

    
    return render_template("gerenciar_usuario.html", usuarios=usuarios, usuario=usuario_selecionado, mensagem=mensagem)

# >>>>>>>>>>>>>>>>>> Manutenção <<<<<<<<<<<<<<<<<<<<
@app.route("/consultar_cliente", methods=["GET", "POST"])
def consultar_cliente():
    clientes_encontrados = []
    mensagem = None

    # Reconstruir árvore de clientes
    arvore_clientes = reconstruir_arvore_clientes()

    if request.method == "POST":
        tipo_busca = request.form.get("tipo_busca")

        # ========================== BUSCA POR CPF ==========================
        if tipo_busca == "cpf":
            cpf = request.form.get("cpf_busca")
            cliente = arvore_clientes.buscar(cpf)

            if cliente:
                clientes_encontrados = [cliente]
            else:
                mensagem = "Nenhum cliente encontrado com esse CPF."

        # ======================= BUSCA PELA INICIAL ========================
        elif tipo_busca == "inicial":
            inicial = request.form.get("inicial").upper()

            todos = arvore_clientes.listar_chaves()
            clientes_encontrados = [
                c for c in todos
                if c.nome.upper().startswith(inicial)
            ]

            if not clientes_encontrados:
                mensagem = f"Nenhum cliente inicia com a letra '{inicial}'."

        # ========================== BUSCA POR NOME =========================
        elif tipo_busca == "nome":
            nome_parcial = request.form.get("nome_busca").upper()

            todos = arvore_clientes.listar_chaves()
            clientes_encontrados = [
                c for c in todos
                if nome_parcial in c.nome.upper()
            ]

            if not clientes_encontrados:
                mensagem = "Nenhum cliente encontrado com esse nome."

    return render_template(
        "consultar_cliente.html",
        clientes=clientes_encontrados,
        mensagem=mensagem
    )



#-----------Rotas para Funçao Extra ----------
@app.route("/chat_bot")
def chat_page():
    return render_template("chat_bot.html")

def get_resposta(msg):
    msg = msg.lower().strip()
    for keys, resposta in respostas.items():
        if msg in keys:
            return resposta
    return "Desculpe, não entendi. Pode reformular?"

@app.route("/voltar_chat")
def voltar_chat():
    # Se for usuário comum
    if session.get("cpf"):
        return redirect(url_for("homeUser"))
    
    # Se não estiver logado (visitante)
    return redirect(url_for("home"))

@app.route("/chat", methods=["POST"])
def chat_bot():
    user_msg = request.get_json().get("message")
    resposta = get_resposta(user_msg)
    return jsonify({"reply": resposta})


#-----------Grafos----------
def criar_grafo_voos(voos):
    g = Graph(directed=True)
    aeroportos = set()
    
    for voo in voos:
        origem = voo.get("Origem")
        destino = voo.get("Destino")
        if origem:
            aeroportos.add(origem)
        if destino:
            aeroportos.add(destino)
    
    g.add_vertices(list(aeroportos))
    indice = {nome: i for i, nome in enumerate(g.vs["name"])}
    
    for voo in voos:
        origem = voo.get("Origem")
        destino = voo.get("Destino")
        if origem and destino:
            g.add_edge(indice[origem], indice[destino])
    
    return g

def criar_imagem_grafo(voos):
    g = criar_grafo_voos(voos)
    
    pasta = os.path.join("static", "img")
    os.makedirs(pasta, exist_ok=True)
    caminho_arquivo = os.path.join(pasta, "grafo.png")
    
    tamanho_vertices = 95  # tamanho fixo para todos os vértices
    cores = ["#4CAF50", "#2196F3", "#FFC107", "#E91E63", "#9C27B0",
             "#FF5722", "#0C0F36", "#360C0C", "#BE1873", "#43768A",
             "#43768A", "#584657", "#584657", "#138F5F", "#495025"]
    cor_vertices = [cores[i % len(cores)] for i in range(len(g.vs))]
    
    layout = g.layout("kk")
    
    visual_style = {
        "vertex_size": tamanho_vertices,
        "vertex_color": cor_vertices,
        "vertex_label": g.vs["name"],  # nome do país dentro da bola
        "vertex_label_color": "white",
        "vertex_label_size": 13, #tamanho da letra 
        "vertex_label_font": "Arial",
        "vertex_label_dist": 0,
        "edge_color": "blue",
        "edge_width": 2,
        "edge_arrow_size": 0.5,
        "edge_arrow_width": 1.5,
        "layout": layout,
        "bbox": (1100, 800),
        "margin": 50
    }
    
    plot(g, target=caminho_arquivo, **visual_style)
    
    return "img/grafo.png"

def buscar_conexoes(origem, destino):
    g = criar_grafo_voos(voos)
    try:
        caminhos = g.get_shortest_paths(origem, to=destino, mode="OUT", output="vpath")
    except:
        return None

    if not caminhos or not caminhos[0]:
        return None

    return [g.vs[i]["name"] for i in caminhos[0]]


@app.route("/grafico_voos")
def grafico_voos():
    imagem_grafo = criar_imagem_grafo(voos)
    return render_template("grafico_voos.html", imagem_grafo=imagem_grafo)


def listar_todos_os_caminhos(origem, destino):
    g = criar_grafo_voos(voos)

    # Mapear nome → índice e índice → nome
    nome_para_indice = {name: i for i, name in enumerate(g.vs["name"])}

    if origem not in nome_para_indice or destino not in nome_para_indice:
        return None

    indice_origem = nome_para_indice[origem]
    indice_destino = nome_para_indice[destino]

    todas_rotas = []
    rota_atual = []

    def dfs(atual):
        rota_atual.append(atual)

        if atual == indice_destino:
            todas_rotas.append(list(rota_atual))
        else:
            for vizinho in g.successors(atual):
                if vizinho not in rota_atual:
                    dfs(vizinho)

        rota_atual.pop()

    dfs(indice_origem)

    rotas_convertidas = []
    for rota in todas_rotas:
        rotas_convertidas.append([g.vs[i]["name"] for i in rota])

    return rotas_convertidas


@app.route("/simular_conexoes/<int:codigo_voo>")
def simular_conexoes(codigo_voo):

    voo = next((v for v in voos if str(v["Codigo_do_voo"]) == str(codigo_voo)), None)
    if voo is None:
        return "Voo não encontrado", 404

    origem = voo["Origem"]
    destino = voo["Destino"]

    caminhos = listar_todos_os_caminhos(origem, destino)

    lista_rotas = []

    for rota in caminhos:
        qtd_paradas = len(rota) - 2
        preco_base = voo["Preco_da_passagem"]

        if qtd_paradas == 0:
            preco_final = preco_base
        else:
            # Desconto progressivo: 10% por parada, até no máximo 50%
            desconto = min(0.1 * qtd_paradas, 0.5)
            preco_final = round(preco_base * (1 - desconto), 2)

        lista_rotas.append({
            "rota": rota,
            "paradas": qtd_paradas,
            "preco": preco_final
        })

    session["rotas_info"] = lista_rotas

    return render_template(
        "simular_conexoes.html",
        origem=origem,
        destino=destino,
        rotas=lista_rotas,
        voo=voo
    )


@app.route("/escolher_rota/<int:codigo_voo>/<int:indice_rota>")
def escolher_rota(codigo_voo, indice_rota):

    rotas = session.get("rotas_info")
    if not rotas:
        return "Erro: rotas não encontradas na sessão", 400

    rota_escolhida = rotas[indice_rota]

    session["rota"] = rota_escolhida["rota"]
    session["preco"] = rota_escolhida["preco"]

    return redirect(url_for("mapaVoo", codigo=codigo_voo))


#-----------Mapa dos paises----------
def criar_mapa_voos(voos, coordenadas):
    mapa = folium.Map(location=[20, 0], zoom_start=2)
    aeroportos_adicionados = set()

    for voo in voos:
        origem = voo.get("Origem")
        destino = voo.get("Destino")
        codigo = voo.get("Codigo_do_voo")
        hora = voo.get("Hora")
        data = voo.get("Data")
        preco = voo.get("Preco_da_passagem")

        # Marcadores
        for aeroporto, cor in [(origem, "green"), (destino, "red")]:
            if aeroporto in coordenadas and aeroporto not in aeroportos_adicionados:
                folium.Marker(
                    location=coordenadas[aeroporto],
                    popup=f"Aeroporto: {aeroporto}",
                    icon=folium.Icon(color=cor, icon="plane")
                ).add_to(mapa)
                aeroportos_adicionados.add(aeroporto)

        # Linha entre aeroportos
        if origem in coordenadas and destino in coordenadas:
            folium.PolyLine(
                locations=[coordenadas[origem], coordenadas[destino]],
                color="blue",
                weight=2,
                opacity=0.7,
                popup=f"Voo {codigo} | Data: {data} | Hora: {hora} | Preço: {preco}"
            ).add_to(mapa)

    mapa.save("templates/mapa_grafico_voos.html")


@app.route("/mapa_grafico_voos")
def mapa_grafico_voos():
    criar_mapa_voos(voos, coordenadas_aeroportos)
    return render_template("mapa_grafico_voos.html")

# >>>>>>>>>>>>>>>>>> Manutenção <<<<<<<<<<<<<<<<<<<<
@app.route("/listar_usuarios")
def listar_usuarios():
    arvore_clientes = reconstruir_arvore_clientes()
    usuarios = arvore_clientes.listar_chaves()
    return render_template("listar_usuarios.html", usuarios=usuarios)

# >>>>>>>>>>>>>>>>>> Manutenção <<<<<<<<<<<<<<<<<<<<
@app.route("/relatorios")
def relatorios():
    arvore_passagens = reconstruir_arvore()
    
    destinos = {}
    voos_realizados = 0
    reservas_totais = 0

    # Cada elemento é um EntradaIndice
    for entrada in arvore_passagens.listar_chaves():
        codigo = entrada.chave   # <-- pegamos a chave de verdade

        reserva = retornarInformacoesRegistro(arvore_passagens, codigo)
        if not reserva:
            continue

        reservas_totais += 1
        voo = next((v for v in voos if str(v["Codigo_do_voo"]) == reserva.codigo_voo), None)
        if voo:
            voos_realizados += 1
            destino = voo["Destino"]
            destinos[destino] = destinos.get(destino, 0) + 1

    destinos_ordenados = sorted(destinos.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        "relatorios.html",
        voos_realizados=voos_realizados,
        reservas_totais=reservas_totais,
        destinos_ordenados=destinos_ordenados
    )


# Rodar a aplicação
if __name__ == "__main__":
    app.run(debug=True)

#python main.py <-- para rodar
