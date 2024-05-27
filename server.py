from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import socket

server_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

server_public_key = server_private_key.public_key()

def receive_message(conn):
    data = conn.recv(1024)
    return data

def send_message(conn, message):
    conn.send(message)

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)

    print("Сервер ожидает подключения...")

    conn, addr = server_socket.accept()

    client_public_key = serialization.load_pem_public_key(
        receive_message(conn),
    )

    send_message(conn, server_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

    while True:
        encrypted_message = receive_message(conn)
        decrypted_message = server_private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print("Получено сообщение от клиента:", decrypted_message.decode())

        message = input("Ответ сервера: ")
        encrypted_response = client_public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        send_message(conn, encrypted_response)

server()
