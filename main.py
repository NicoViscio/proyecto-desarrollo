import sys
from PyQt5.QtWidgets import QApplication
from model.user_model import UserModel
from view.login_view import LoginView
from controller.controller import Controller

# se crean las instancias del modelo, la vista y el controlador, y se lanza la interfaz gráfica.
if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = UserModel()
    view = LoginView()
    controller = Controller(model, view)

    view.show()
    sys.exit(app.exec_())
