from PyQt5.QtWidgets import QMessageBox
from model.user_model import UserModel
from model.chat_model import ChatModel
from view.login_view import LoginView
from view.chat_view import ChatView
import threading
import os

class Controller:
    def __init__(self, model, view):
        self.model = model          # Modelo que almacena el nombre del usuario
        self.view = view            # Vista de login
        self.view.button.clicked.connect(self.start_chat)  # Conecta botón de login con el método start_chat

        self.chat_view = None       # Se inicializará al pasar a la vista de chat
        self.chat_model = None      # Modelo de red (cliente/servidor) para el chat

    def start_chat(self):
        """Maneja el inicio del chat: valida el nombre, establece conexión y abre la vista de chat."""
        username = self.view.get_username()
        if username.strip() == "":
            # Muestra advertencia si el nombre está vacío
            QMessageBox.warning(self.view, "Error", "Por favor, introduce un nombre.")
            return

        self.model.set_username(username)
        print(f"[DEBUG] Nombre introducido: {self.model.get_username()}")

        # Inicializa el modelo de chat con el nombre
        self.chat_model = ChatModel(username)

        # Intenta conectarse como cliente
        try:
            self.chat_model.start_client()
            self.is_server = False
            print("[DEBUG] Se ha conectado como cliente.")
        except Exception as e:
            # Si falla, inicia como servidor
            print(f"[DEBUG] Fallo como cliente, iniciando como servidor: {e}")
            try:
                self.chat_model.start_server()
                self.is_server = True
                print("[DEBUG] Se ha iniciado como servidor.")
            except Exception as e2:
                # Si falla también como servidor, muestra error y termina
                QMessageBox.warning(self.view, "Error", f"No se pudo iniciar como cliente ni como servidor:\nCliente: {e}\nServidor: {e2}")
                return

        # Cierra vista de login y abre la vista de chat
        self.view.close()
        self.chat_view = ChatView(username)

        # Conecta los botones de enviar mensaje e imagen con sus funciones
        self.chat_view.send_button.clicked.connect(self.send_message)
        self.chat_view.image_button.clicked.connect(self.upload_image)
        self.chat_view.show()

        # Inicia hilo para recibir mensajes de forma continua
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self):
        """Envía un mensaje de texto al otro usuario."""
        msg = self.chat_view.get_message().strip()
        if msg == "":
            return

        full_msg = f"{self.model.get_username()}: {msg}"
        try:
            self.chat_model.send_message(full_msg)            # Envía mensaje por red
            self.chat_view.display_message(full_msg)          # Muestra mensaje localmente
            self.chat_view.clear_input()                      # Limpia el campo de entrada
        except Exception as e:
            QMessageBox.warning(self.chat_view, "Error", f"No se pudo enviar el mensaje: {e}")

    def upload_image(self):
        """Permite seleccionar y enviar una imagen."""
        try:
            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(
                self.chat_view, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            
            if file_path:
                if not os.path.exists(file_path):
                    QMessageBox.warning(self.chat_view, "Error", "El archivo seleccionado no existe.")
                    return

                # Formato del mensaje de imagen
                full_msg = f"{self.model.get_username()}: {file_path}"
                try:
                    self.chat_model.send_message(f"IMG:{file_path}")           # Enviar como imagen
                    self.chat_view.display_image_from_path(full_msg)           # Mostrar imagen en interfaz
                except Exception as e:
                    QMessageBox.warning(self.chat_view, "Error", f"No se pudo enviar la imagen: {e}")
        except Exception as e:
            QMessageBox.warning(self.chat_view, "Error", f"Error al procesar la imagen: {e}")

    def receive_messages(self):
        #Hilo que recibe mensajes del otro usuario y los muestra en pantalla.
        while True:
            try:
                msg = self.chat_model.receive_message()
                if msg:
                    # Emite señal para mostrar texto o imagen dependiendo del tipo
                    self.chat_view.new_message_signal.emit(msg)
            except Exception as e:
                print(f"[ERROR] Error recibiendo mensajes: {e}")
                break
