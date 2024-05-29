import socket
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Генерация пары ключей (приватный и публичный)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# Сериализация публичного ключа в формат PEM
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


# Установка соединения на порту 12345 для передачи публичного ключа и установления режима шифрования
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(1)

print("Ждем подключения для установления режима шифрования...")
connection, address = server_socket.accept()
print("Подключение установлено:", address)

connection.send(public_pem)

# Получение номера порта для основного общения
port_number = int(connection.recv(1024).decode())
print("Номер порта для основного общения:", port_number)

# Закрытие соединения для установления режима шифрования
connection.close()
server_socket.close()

# Установление основного соединения на указанном порту для общения
main_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_server_socket.bind(('localhost', port_number))
main_server_socket.listen(1)

print("Ждем подключения для основного общения...")
main_connection, main_address = main_server_socket.accept()
print("Подключение для основного общения установлено:", main_address)

# Использование ключей для шифрования и дешифрования сообщений
while True:
    data = main_connection.recv(1024)
    if not data:
        break
    decrypted_message = private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print("Получено зашифрованное сообщение:", decrypted_message.decode())

main_connection.close()
main_server_socket.close()
