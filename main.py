from flask import Flask, render_template, request, redirect, url_for #importando a classe Flask do pacote Flask

app = Flask(__name__)  # cria a aplicação

#dicionario de clientes
usuarios = {
    "felipe@gmail.com": {"senha": "12345", "nome": "Felipe Cerqueira"},
    "Larissa@gmail.com": {"senha": "12345", "nome": "Larissa"},
    "Joao@gmail.com": {"senha": "12345", "nome": "Joao"}
}

@app.route("/")        # define uma rota
def home():
    return render_template("home.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    mensagem = None
    email = ""
    senha = ""

    if request.method == "POST": # só processa se o form for enviado 
        email = request.form.get("email")
        senha = request.form.get("senha")

    # Verifica se o e-mail existe e se a senha está correta
    if email in usuarios and usuarios[email]["senha"] == senha:
         # Redireciona para home e envia o nome do usuário
         nome = usuarios[email]["nome"]
         return redirect(url_for("home", usuario=nome))

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)

#python main.py <-- para rodar
