class Cliente:
    def __init__(self, cpf, nome, reservas=None, datas=None, milhas=0):
        self.cpf = cpf
        self.nome = nome
        self.reservas = reservas or []
        self.datas = datas or []
        self.milhas = milhas

    def __repr__(self):
        return f"{self.cpf} - {self.nome}"
