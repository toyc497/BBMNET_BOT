class CredencialEntity:
    def __init__(self, id, usuario, senha, sistema):
        self.id = id
        self.usuario = usuario
        self.senha = senha
        self.sistema = sistema

    def __str__(self):
        return f"id: {self.id}, usuario: {self.usuario}, senha: {self.senha}, sistema: {self.sistema}"