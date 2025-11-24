class RegistroPassagem:
    def __init__(self, codigo_passagem, cpf, codigo_voo, assento, preco=None, rota=None):
        self.codigo_passagem = codigo_passagem
        self.cpf = cpf
        self.codigo_voo = codigo_voo
        self.assento = assento
        self.preco = preco          # novo atributo
        self.rota = rota or []      # lista com as cidades da rota

    def __repr__(self):
        return (
            f"(Passagem: {self.codigo_passagem}, CPF: {self.cpf}, "
            f"Voo: {self.codigo_voo}, Assento: {self.assento}, "
            f"Preço: {self.preco}, Rota: {self.rota})"
        )
