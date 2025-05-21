from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class LoginView(QWidget):
    def __init__(self):
        #Esta interfaz permite al usuario introducir su nombre antes de acceder al chat.
        #Configura el diseño, los estilos y los componentes de la interfaz gráfica.
        super().__init__()
        self.setWindowTitle("Chat local - LNVF")
        self.setFixedSize(300, 200)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 16px;
                color: #333;
                margin-bottom: 15px;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-bottom: 30px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        # Inicialización y configuración del layout principal vertical
        self.layout = QVBoxLayout()

        # Etiqueta con la instrucción al usuario
        self.label = QLabel("Introduce tu nombre de usuario:")
        self.label.setAlignment(Qt.AlignCenter)
        # Campo de entrada para el nombre de usuario
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tu nombre...")

        # Botón para confirmar el inicio del chat
        self.button = QPushButton("Iniciar Chat")

        # Añadimos estiramientos para centrar verticalmente los widgets
        self.layout.addStretch()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.button)
        self.layout.addStretch()

        # Aplicamos el layout principal a la ventana
        self.setLayout(self.layout)

    def get_username(self):
        return self.username_input.text()
