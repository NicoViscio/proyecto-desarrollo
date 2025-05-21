class UserModel:
    def __init__(self):
        # Inicializa el atributo que almacenará el nombre de usuario
        self.username = ""

    def set_username(self, name):
        # Establece el nombre de usuario.
        self.username = name

    def get_username(self):
        # Retorna el nombre de usuario actual.
        return self.username
