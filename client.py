from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import socket

client_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

client_public_key = client_private_key.public_key()

def receive_message(conn):
    data = conn.recv(1024)
    return data

def send_message(conn, message):
    conn.send(message)

def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))

    send_message(client_socket, client_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

    server_public_key = serialization.load_pem_public_key(
        receive_message(client_socket),
    )

    while True:
        message = input("Сообщение для сервера: ")
        encrypted_message = server_public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        send_message(client_socket, encrypted_message)

        encrypted_response = receive_message(client_socket)
        decrypted_response = client_private_key.decrypt(
            encrypted_response,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print("Ответ от сервера:", decrypted_response.decode())

client()
