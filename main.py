from flask import Flask, render_template, request, redirect, url_for #importando a classe Flask do pacote Flask
from arquivos.usuarios import usuarios # chamando o arquivo de usuarios
from arquivos.voos import voos # chamando o arquivo de usuarios

app = Flask(__name__)  # cria a aplicação

# Definindo Rotas
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/reservar_voo")   
def reserva():
    return render_template("reservar_voo.html", voos_agendados = voos)

@app.route("/login", methods = ["GET", "POST"])
def login():
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

    return render_template("login.html", mensagem=mensagem)


# Rodar a aplicação
if __name__ == "__main__":
    app.run(debug=True)

#python main.py <-- para rodar
