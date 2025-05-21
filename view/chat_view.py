from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                           QLabel, QScrollArea, QFrame, QFileDialog, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent  
from PIL import Image
import io
import base64
import os

class ChatView(QWidget):
    new_message_signal = pyqtSignal(str)

    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Chat local - LNVF")
        self.username = username
        self.new_message_signal.connect(self.display_message)
        self.setGeometry(100, 100, 500, 600)
        self.setup_ui()
        
        # Inicializamos el sistema de sonido
        self.setup_notification_sound()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # NUEVO: Título "Chat con: nombre"
        self.chat_title_label = QLabel(f"Chat con: {self.username}")
        self.chat_title_label.setAlignment(Qt.AlignCenter)
        self.chat_title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                color: #333;
            }
        """)
        self.layout.addWidget(self.chat_title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_container)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Escribe un mensaje...")

        self.send_button = QPushButton("⬆️")
        self.send_button.setFixedWidth(40)
        self.send_button.setFixedHeight(36)
        self.send_button.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        self.emoji_button = QPushButton("😀")  # Botón para abrir emojis
        self.emoji_button.setFixedWidth(40)
        self.emoji_button.setFixedHeight(36)
        self.emoji_button.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        # Botón para subir imágenes
        self.image_button = QPushButton("📷")
        self.image_button.setFixedWidth(40)
        self.image_button.setFixedHeight(36)
        self.image_button.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        # Panel oculto de emojis
        self.emoji_panel = QWidget()
        self.emoji_panel.setWindowFlags(Qt.Popup)
        emoji_layout = QHBoxLayout(self.emoji_panel)
        emojis = ['😀', '😂', '😍', '👍', '🙏', '🎉']
        for e in emojis:
            btn = QPushButton(e)
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("font-size: 20px; border: none; background: transparent;")
            btn.clicked.connect(lambda checked, emoji=e: self.insert_emoji(emoji))
            emoji_layout.addWidget(btn)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.message_input)
        bottom_layout.addWidget(self.emoji_button)
        bottom_layout.addWidget(self.image_button)
        bottom_layout.addWidget(self.send_button)

        self.layout.addWidget(self.scroll_area)
        self.layout.addLayout(bottom_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #eaeaea;
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                padding: 8px 12px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        self.emoji_button.clicked.connect(self.toggle_emoji_panel)

    def setup_notification_sound(self):
        """Inicializa el sistema de sonido de notificación"""
        # Creamos el reproductor de medios
        self.media_player = QMediaPlayer()
        
        # Buscamos el archivo de sonido en varias ubicaciones posibles
        sound_file_name = "notification.mp3"  # Puede ser .mp3, .wav, etc.
        
        # Primero buscamos en el directorio de la aplicación
        app_dir = os.path.dirname(os.path.abspath(__file__))
        sound_paths = [
            os.path.join(app_dir, sound_file_name),  # En el directorio de la app
            os.path.join(app_dir, "sounds", sound_file_name),  # En subdirectorio sounds
        ]
        
        # La ruta del archivo de sonido que usaremos
        self.notification_sound_path = None
        
        # Buscar el archivo en las rutas posibles
        for path in sound_paths:
            if os.path.exists(path):
                self.notification_sound_path = path
                break
        
        if not self.notification_sound_path:
            print("[ADVERTENCIA] No se encontró el archivo de sonido.")
            print(f"Por favor, añade un archivo llamado '{sound_file_name}' en la carpeta de la aplicación.")
    
    def play_notification_sound(self):
        """Reproduce el sonido de notificación"""
        try:
            if self.notification_sound_path and os.path.exists(self.notification_sound_path):
                # Establecer el archivo de audio
                media_content = QMediaContent(QUrl.fromLocalFile(self.notification_sound_path))
                self.media_player.setMedia(media_content)
                # Reproducir
                self.media_player.play()
            else:
                print("[ADVERTENCIA] No se puede reproducir el sonido: archivo no encontrado")
        except Exception as e:
            print(f"[ERROR] Error al reproducir el sonido de notificación: {e}")

    def toggle_emoji_panel(self):
        if self.emoji_panel.isVisible():
            self.emoji_panel.hide()
        else:
            # Posicionar el panel justo encima del botón de emojis
            pos = self.emoji_button.mapToGlobal(self.emoji_button.rect().bottomLeft())
            self.emoji_panel.move(pos.x(), pos.y())
            self.emoji_panel.show()

    def insert_emoji(self, emoji):
        cursor_pos = self.message_input.cursorPosition()
        text = self.message_input.text()
        new_text = text[:cursor_pos] + emoji + text[cursor_pos:]
        self.message_input.setText(new_text)
        self.message_input.setCursorPosition(cursor_pos + len(emoji))
        self.message_input.setFocus()
        self.emoji_panel.hide()

    def chat_view_signal_image(self, file_path):
        # Esta función se conectará en el controller para manejar el envío de imágenes
        try:
            # Crear un mensaje especial indicando que es una imagen
            msg = f"IMG:{file_path}"
            # Este es un mensaje indicando que se está enviando una imagen
            # El formato "IMG:" se utilizará para identificar mensajes de imagen
            from PyQt5.QtCore import pyqtSignal
            # Emitir señal que será capturada por el controller
            self.new_message_signal.emit(msg)
        except Exception as e:
            print(f"Error al señalizar la imagen: {e}")

    def display_message(self, msg):
        # Primero determinamos si el mensaje es propio o recibido
        is_self = False
        if ":" in msg:
            sender = msg.split(":", 1)[0]
            is_self = sender == self.username or sender == "Yo"
        
        # Reproducimos el sonido SOLO si el mensaje NO es propio
        if not is_self:
            self.play_notification_sound()
            
        # Comprobamos si es un mensaje de imagen
        if msg.startswith("IMG:"):
            # Extraemos la ruta o datos de la imagen
            img_data = msg[4:]
            if img_data.startswith("DATA:"):
                # Es una imagen codificada en base64
                img_base64 = img_data[5:]
                self.display_image_from_base64(img_base64)
            else:
                # Es una ruta de archivo
                self.display_image_from_path(msg)
            return
        
        # Si no es una imagen, procesamos como mensaje normal
        is_self = msg.startswith(f"{self.username}:")
        
        # Modificamos el mensaje para mostrar "Yo:" en lugar del nombre de usuario
        if is_self:
            prefix = f"{self.username}:"
            msg = "Yo:" + msg[len(prefix):]
            
        bubble = self.create_message_bubble(msg, is_self)

        bubble_layout = QHBoxLayout()
        if is_self:
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble)
        else:
            bubble_layout.addWidget(bubble)
            bubble_layout.addStretch()

        container = QWidget()
        container.setLayout(bubble_layout)
        self.chat_layout.addWidget(container)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def display_image_from_path(self, file_path):
        try:
            # Determinamos si el mensaje es propio o de otro usuario
            is_self = False
            actual_path = ""
            
            # Si es un mensaje con formato de nombre: ruta
            if ":" in file_path:
                parts = file_path.split(":", 1)
                sender = parts[0]
                is_self = sender == self.username
                
                if file_path.startswith("IMG:"):
                    # Si empieza con IMG: es porque viene directamente del controller
                    actual_path = file_path[4:]
                elif len(parts) > 1:
                    # Es un mensaje normal con nombre: ruta
                    actual_path = parts[1].strip()
            else:
                # Si no tiene formato, asumimos que es la ruta directa
                actual_path = file_path
            
            # Si la ruta empieza con IMG: debemos quitarlo también
            if actual_path.startswith("IMG:"):
                actual_path = actual_path[4:]
                
            # Verificamos que el archivo existe
            if not os.path.exists(actual_path):
                print(f"[ERROR] El archivo de imagen no existe: {actual_path}")
                self.display_message(f"Error: No se pudo cargar la imagen {actual_path}")
                return
            
            # Si es un mensaje propio, añadimos una etiqueta para mostrar "Yo" en lugar del nombre
            sender_label = None
            if is_self:
                sender_label = QLabel("Yo:")
                sender_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        color: #333;
                        margin-right: 5px;
                    }
                """)
            elif ":" in file_path:
                # Mostrar el nombre del remitente para mensajes de otros
                sender_name = parts[0]
                if sender_name != "IMG":  # Evitamos mostrar "IMG:" como nombre
                    sender_label = QLabel(f"{sender_name}:")
                    sender_label.setStyleSheet("""
                        QLabel {
                            font-weight: bold;
                            color: #333;
                            margin-right: 5px;
                        }
                    """)
                
            pixmap = QPixmap(actual_path)
            if pixmap.width() > 300:
                pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
            
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {'#d4f8d4' if is_self else '#add8e6'};
                    padding: 10px;
                    border-radius: 10px;
                }}
            """)
            
            # Creamos un layout para la burbuja de mensaje
            bubble_layout = QHBoxLayout()
            
            # Layout vertical para contener la etiqueta del remitente y la imagen
            if sender_label:
                message_container = QVBoxLayout()
                message_container.addWidget(sender_label)
                message_container.addWidget(image_label)
                message_container.setAlignment(Qt.AlignTop)
                
                # Creamos un widget para contener este layout vertical
                msg_widget = QWidget()
                msg_widget.setLayout(message_container)
                
                if is_self:
                    bubble_layout.addStretch()
                    bubble_layout.addWidget(msg_widget)
                else:
                    bubble_layout.addWidget(msg_widget)
                    bubble_layout.addStretch()
            else:
                # Si no hay etiqueta de remitente, solo añadimos la imagen
                if is_self:
                    bubble_layout.addStretch()
                    bubble_layout.addWidget(image_label)
                else:
                    bubble_layout.addWidget(image_label)
                    bubble_layout.addStretch()

            container = QWidget()
            container.setLayout(bubble_layout)
            self.chat_layout.addWidget(container)
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        except Exception as e:
            print(f"Error al mostrar la imagen desde archivo: {e}")
            self.display_message(f"Error al mostrar la imagen: {e}")

    def display_image_from_base64(self, img_base64):
        try:
            # Decodificamos la imagen desde base64
            img_data = base64.b64decode(img_base64)
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            
            if pixmap.width() > 300:
                pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
            
            # Determinamos si el mensaje es propio o de otro usuario
            # Para mensajes en base64, necesitaríamos información adicional para
            # saber si es un mensaje propio o recibido
            is_self = False  # Por defecto asumimos que no es propio
            
            # Podemos añadir una etiqueta con el nombre del remitente
            sender_label = None
            if not is_self:
                sender_label = QLabel("Foto:")
                sender_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        color: #333;
                        margin-right: 5px;
                    }
                """)
            
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {'#d4f8d4' if is_self else '#add8e6'};
                    padding: 10px;
                    border-radius: 10px;
                }}
            """)
            
            bubble_layout = QHBoxLayout()
            
            # Si hay etiqueta de remitente, creamos un layout vertical
            if sender_label:
                message_container = QVBoxLayout()
                message_container.addWidget(sender_label)
                message_container.addWidget(image_label)
                message_container.setAlignment(Qt.AlignTop)
                
                msg_widget = QWidget()
                msg_widget.setLayout(message_container)
                
                if is_self:
                    bubble_layout.addStretch()
                    bubble_layout.addWidget(msg_widget)
                else:
                    bubble_layout.addWidget(msg_widget)
                    bubble_layout.addStretch()
            else:
                # Si no hay etiqueta, solo añadimos la imagen
                if is_self:
                    bubble_layout.addStretch()
                    bubble_layout.addWidget(image_label)
                else:
                    bubble_layout.addWidget(image_label)
                    bubble_layout.addStretch()

            container = QWidget()
            container.setLayout(bubble_layout)
            self.chat_layout.addWidget(container)
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        except Exception as e:
            print(f"Error al mostrar la imagen desde base64: {e}")
            self.display_message(f"Error al mostrar la imagen: {e}")

    def create_message_bubble(self, msg, is_self):
        label = QLabel(msg)
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            QLabel {{
                background-color: {'#d4f8d4' if is_self else '#add8e6'};
                padding: 10px;
                border-radius: 10px;
                max-width: 300px;
            }}
        """)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        return label

    def get_message(self):
        return self.message_input.text()

    def clear_input(self):
        self.message_input.clear()