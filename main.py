from flask import Flask, render_template, request, redirect, url_for, jsonify, session #importando a classe Flask do pacote Flask
from arquivos.manipular_usuarios import carregar_usuarios, salvar_usuarios # chamando o arquivo de usuarios
from arquivos.manipular_voos import carregar_voos, salvar_voos # chamando as funções para manipular o arquivo
from arquivos.manipular_adm import carregar_adms, salvar_adms
from arquivos.manipular_VendasPassagens import carregar_registros_passagens, salvar_registros_passagens
from arquivos.ArvoreB_VendaPassagens import arvore, reconstruir_arvore
from arquivos.manipular_Informacoes import carregar_valor, salvar_valor
from arquivos.manipular_Reservas import carregar_reservas, salvar_reservas
from arquivos.ArvoreB_VendaPassagens import RegistroPassagem


from arquivos.respostas import respostas

from arquivos.respostas import respostas
import os
from igraph import Graph, plot
import folium
from arquivos.manipular_coordenadas import carregar_coordenadas

coordenadas_aeroportos = carregar_coordenadas()

app = Flask(__name__)  # cria a aplicação


app.secret_key = "123456"

voos = carregar_voos()
adms = carregar_adms()
usuarios = carregar_usuarios()
reservas = carregar_reservas()
valor = carregar_valor()
print(valor)


# Definindo Rotas
@app.route("/")
def home():
    return render_template("home.html")

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

    return render_template("confirmarReserva.html", voo=voo, assento=assento)

@app.route("/reservar_assento/<codigo>/<int:assento>", methods=["POST"])
def reservar_assento(codigo, assento):
    global valor  # necessário para alterar a variável global

    voo = next((v for v in voos if str(v["Codigo_do_voo"]) == codigo), None)
    if voo is None:
        return "Voo não encontrado", 404

    if str(assento) not in voo["Assentos_ocupados"]:
        # Marca assento como ocupado
        voo["Assentos_ocupados"].append(str(assento))
        salvar_voos(voos)

        # Incrementa o valor da passagem
        valor += 1
        salvar_valor(valor)  # salva no arquivo o novo valor

        # Cria reserva
        registro = RegistroPassagem(
           codigo_passagem=valor,
           cpf=session.get("cpf"),
           codigo_voo= codigo,
           assento=str(assento)
         )

        arvore.inserir(registro)

        reservas.append({
         "codigo_passagem": registro.codigo_passagem,
         "cpf": registro.cpf,
         "codigo_voo": registro.codigo_voo,
         "assento": registro.assento
         })
        salvar_reservas(reservas)

    return "", 204  # não retorna conteúdo

@app.route("/minhas_reservas")
def minhas_reservas():
    cpf = session.get("cpf")
    if not cpf:
        return redirect(url_for("login_user"))

    reservas = []
    voos_encontrados = []

    # percorre todos os objetos da árvore:
    registros = arvore.listar_chaves()
    if not registros:
        print("lista vazia")
    
    for registro in registros:
        reserva = arvore.buscar(registro.codigo_passagem)
        if reserva and reserva.cpf == cpf:
            reservas.append(reserva)

            voo = next((v for v in voos if v["Codigo_do_voo"] == reserva.codigo_voo), None)
            if voo:
                voos_encontrados.append(voo)

    return render_template("minhas_reservas.html", reservas_usuario = reservas, voos_encontrados = voos_encontrados)

@app.route("/cancelar_reserva/<int:codigo_passagem>")
def cancelar_reserva(codigo_passagem):
    cpf = session.get("cpf")
    if not cpf:
        return redirect(url_for("login_user"))

    # 1. Buscar a reserva na árvore B
    reserva = arvore.buscar(codigo_passagem)

    if not reserva:
        return redirect(url_for("minhas_reservas"))

    # 2. Liberar o assento no voo
    codigo_voo = reserva.codigo_voo
    assento = reserva.assento

    voo = next((v for v in voos if v["Codigo_do_voo"] == codigo_voo), None)

    if voo and assento in voo["Assentos_ocupados"]:
        voo["Assentos_ocupados"].remove(assento)

    # 3. Remover do arquivo reservas
    reservas = carregar_reservas()

    reservas = [
        r for r in reservas 
        if r.get("codigo_passagem") != codigo_passagem
    ]

    salvar_reservas(reservas)
    arvore = reconstruir_arvore()

    return redirect(url_for("minhas_reservas"))




@app.route("/InicialAdm")   
def editar():
    if "email" not in session:
        return redirect(url_for("login_adm"))  # bloqueia acesso direto
    return render_template("InicialAdm.html", voos_agendados = voos, email=session["email"])

@app.route("/login_user", methods = ["GET", "POST"])
def login_user():
    mensagem = "" # só processa se o form for enviado 
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Verifica email e senha
        for usuario in usuarios:
            if usuario["email"] == email and usuario["senha"] == senha:
                session["email"] = email  # guarda na sessão
                session["cpf"] = usuario["cpf"] 
                return redirect(url_for("homeUser")) 
            
        mensagem = "Email ou senha incorretos!"

    return render_template("login_user.html", mensagem=mensagem)


@app.route("/homeUser")
def homeUser():
    return render_template("homeUser.html", email=session["email"])

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
            "Assentos_ocupados": []
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



@app.route("/chat_bot")
def chat_page():
    return render_template("chat_bot.html")


def get_resposta(msg):
    msg = msg.lower().strip()
    for keys, resposta in respostas.items():
        if msg in keys:
            return resposta
    return "Desculpe, não entendi. Pode reformular?"

@app.route("/chat", methods=["POST"])
def chat_bot():
    user_msg = request.get_json().get("message")
    resposta = get_resposta(user_msg)
    return jsonify({"reply": resposta})









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
    
    tamanho_vertices = 90  # tamanho fixo para todos os vértices
    cores = ["#4CAF50", "#2196F3", "#FFC107", "#E91E63", "#9C27B0", "#FF5722", "#0C0F36", "#360C0C", "#BE1873"]
    cor_vertices = [cores[i % len(cores)] for i in range(len(g.vs))]
    
    layout = g.layout("kk")
    
    visual_style = {
        "vertex_size": tamanho_vertices,
        "vertex_color": cor_vertices,
        "vertex_label": g.vs["name"],  # nome do país dentro da bola
        "vertex_label_color": "white",
        "vertex_label_size": 12,
        "vertex_label_font": "Arial",
        "vertex_label_dist": 0,
        "edge_color": "blue",
        "edge_width": 2,
        "edge_arrow_size": 0.5,
        "edge_arrow_width": 1.5,
        "layout": layout,
        "bbox": (1000, 800),
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




@app.route("/simular_conexoes", methods=["GET", "POST"])
def simular_conexoes():
    aeroportos = sorted({v.get("Origem") for v in voos if v.get("Origem")} |
                        {v.get("Destino") for v in voos if v.get("Destino")})

    caminho = None
    origem = None
    destino = None

    if request.method == "POST":
        origem = request.form.get("origem")
        destino = request.form.get("destino")
        caminho = buscar_conexoes(origem, destino)

    return render_template(
        "simular_conexoes.html",
        aeroportos=aeroportos,
        origem=origem,
        destino=destino,
        caminho=caminho
    )







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







# Rodar a aplicação
if __name__ == "__main__":
    app.run(debug=True)

#python main.py <-- para rodar
