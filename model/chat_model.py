import socket
import threading
import base64
from PIL import Image
import io
import os

# Modelo que gestiona la comunicación cliente-servidor y el envío/recepción de mensajes e imágenes
class ChatModel:
    def __init__(self, username):
        self.username = username  # Nombre del usuario
        self.sock = None          # Socket principal
        self.conn = None          # Socket de conexión entrante (modo servidor)
        self.addr = None          # Dirección del cliente conectado (modo servidor)
        self.is_server = False    # Indicador de modo (cliente o servidor)
        self.max_buffer_size = 10 * 1024 * 1024  # Límite de tamaño de recepción (10MB)

    # Inicia el modelo en modo servidor
    def start_server(self, host='localhost', port=12345):
        self.is_server = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(1)
        print("[DEBUG] Servidor esperando conexión...")
        self.conn, self.addr = self.sock.accept()
        print(f"[DEBUG] Conexión establecida con {self.addr}")

    # Intenta conectar como cliente
    def start_client(self, host='localhost', port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print("[DEBUG] Cliente conectado al servidor")

    # Enviar mensaje (texto o imagen según el prefijo)
    def send_message(self, msg):
        if msg.startswith("IMG:"):
            self._send_image(msg[4:])  # Se extrae la ruta de imagen y se envía
        else:
            self._send_text(msg)      # Se envía texto normal

    # Envío de mensaje de texto con prefijo 'TEXT:'
    def _send_text(self, msg):
        if self.is_server:
            self.conn.sendall(f"TEXT:{msg}".encode())
        else:
            self.sock.sendall(f"TEXT:{msg}".encode())

    # Envío de imagen codificada en base64
    def _send_image(self, img_path):
        try:
            if not os.path.exists(img_path):
                print(f"[ERROR] El archivo {img_path} no existe.")
                return

            # Abre y opcionalmente redimensiona la imagen
            with Image.open(img_path) as img:
                if img.width > 800 or img.height > 600:
                    img.thumbnail((800, 600))  # Redimensionar manteniendo proporciones

                buffer = io.BytesIO()
                img.save(buffer, format=img.format or 'PNG')
                img_bytes = buffer.getvalue()
                
                # Codifica en base64
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                full_message = f"IMG:DATA:{img_base64}"

                # Envía como string
                if self.is_server:
                    self.conn.sendall(full_message.encode('utf-8'))
                else:
                    self.sock.sendall(full_message.encode('utf-8'))

                print(f"[DEBUG] Imagen enviada: {len(img_base64)} bytes")
        except Exception as e:
            print(f"[ERROR] Error al enviar imagen: {e}")

    # Recepción de mensaje (texto o imagen)
    def receive_message(self):
        try:
            # Lee encabezado (los primeros 5 caracteres)
            if self.is_server:
                header = self.conn.recv(5).decode('utf-8')
            else:
                header = self.sock.recv(5).decode('utf-8')

            if not header:
                return None

            # Según el encabezado, determina el tipo de mensaje
            if header == "TEXT:":
                return self._receive_text(header)
            elif header == "IMG:D":
                # Leer los siguientes 4 bytes "ATA:" para completar "IMG:DATA:"
                if self.is_server:
                    self.conn.recv(4)
                else:
                    self.sock.recv(4)
                return self._receive_image()
            else:
                # Formato antiguo o inesperado
                return self._receive_legacy_message(header)
        except ConnectionError:
            print("[DEBUG] Conexión cerrada.")
            return None
        except Exception as e:
            print(f"[ERROR] Error recibiendo mensaje: {e}")
            return None

    # Recepción de mensaje de texto
    def _receive_text(self, header_already_read):
        if self.is_server:
            data = self.conn.recv(1024)
        else:
            data = self.sock.recv(1024)

        if not data:
            return None

        full_message = header_already_read + data.decode('utf-8')
        return full_message[5:]  # Retirar "TEXT:"

    # Recepción de mensaje de imagen codificada
    def _receive_image(self):
        chunks = []
        bytes_received = 0

        while bytes_received < self.max_buffer_size:
            if self.is_server:
                chunk = self.conn.recv(8192)
            else:
                chunk = self.sock.recv(8192)

            if not chunk:
                break

            chunks.append(chunk)
            bytes_received += len(chunk)

            if len(chunk) < 8192:
                break  # Se ha recibido todo

        data = b''.join(chunks)
        img_base64 = data.decode('utf-8')

        return f"IMG:DATA:{img_base64}"

    # Método de compatibilidad con formatos antiguos
    def _receive_legacy_message(self, partial_data):
        if self.is_server:
            data = self.conn.recv(1024)
        else:
            data = self.sock.recv(1024)

        if not data:
            return None

        return partial_data + data.decode('utf-8')

    # Cierre seguro de sockets
    def close(self):
        if self.is_server:
            self.conn.close()
            self.sock.close()
        else:
            self.sock.close()
