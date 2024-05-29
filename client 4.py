import socket
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Установление соединения с сервером на порту 12345 для получения публичного ключа и установления режима шифрования
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))

public_key_pem = client_socket.recv(1024)
public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())

# Отправка номера порта для основного общения
main_port_number = 54321  # Пример номера порта для основного общения
client_socket.send(str(main_port_number).encode())

client_socket.close()

# Установление основного соединения на указанном порту для общения
main_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_client_socket.connect(('localhost', main_port_number))

# Шифрование и отправка сообщений
message = b"Hello, Server!"
encrypted_message = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
main_client_socket.send(encrypted_message)

main_client_socket.close()
