from flask import Flask, render_template, request, redirect, url_for #importando a classe Flask do pacote Flask
from arquivos.manipular_usuarios import carregar_usuarios, salvar_usuarios # chamando o arquivo de usuarios
from arquivos.manipular_voos import carregar_voos, salvar_voos # chamando as funções para manipular o arquivo
from arquivos.manipular_adm import carregar_adms, salvar_adms
from arquivos.manipular_VendasPassagens import carregar_registros_passagens, salvar_registros_passagens
from arquivos.ArvoreB_VendaPassagens import arvore

app = Flask(__name__)  # cria a aplicação

voos = carregar_voos()
adms = carregar_adms()
usuarios = carregar_usuarios()

# Definindo Rotas
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/reservar_voo")   
def reserva():
    return render_template("reservar_voo.html", voos_agendados = voos)

@app.route("/InicialAdm")   
def editar():
    return render_template("InicialAdm.html", voos_agendados = voos)

@app.route("/login_user", methods = ["GET", "POST"])
def login_user():
    mensagem = "" # só processa se o form for enviado 
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Verifica email e senha
        for usuario in usuarios:
            if usuario["email"] == email and usuario["senha"] == senha:
                return redirect(url_for("reserva"))
            else:
                mensagem = "Email ou senha incorretos!"

    return render_template("login_user.html", mensagem=mensagem)


@app.route("/login_adm", methods = ["GET", "POST"])
def login_adm():
    mensagem = "" # só processa se o form for enviado 
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Verifica email e senha
        for adm in adms:
            if adm["email"] == email and adm["senha"] == senha:
                return redirect(url_for("editar"))
            else:
                mensagem = "Email ou senha incorretos!"

    return render_template("login_adm.html", mensagem=mensagem)


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
            "Data": data
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
def chat_bot():
    return render_template("chat_bot.html")


# Rodar a aplicação
if __name__ == "__main__":
    app.run(debug=True)

#python main.py <-- para rodar
