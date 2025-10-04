from flask import Flask, render_template #importando a classe Flask do pacote Flask

app = Flask(__name__)  # cria a aplicação

@app.route("/")        # define uma rota
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)


#python main.py <-- para rodar
