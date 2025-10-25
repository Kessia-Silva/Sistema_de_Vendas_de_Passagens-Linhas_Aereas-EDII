from flask import Flask, render_template, request, redirect, url_for #importando a classe Flask do pacote Flask
from arquivos.usuarios import usuarios # chamando o arquivo de usuarios
from arquivos.voos import voos # chamando o arquivo de voos
from arquivos.adm import adms

app = Flask(__name__)  # cria a aplicação

# Definindo Rotas
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/reservar_voo")   
def reserva():
    return render_template("reservar_voo.html", voos_agendados = voos)

@app.route("/editar_voos")   
def editar():
    return render_template("editar_voo.html", voos_agendados = voos)

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


# Rodar a aplicação
if __name__ == "__main__":
    app.run(debug=True)

#python main.py <-- para rodar
