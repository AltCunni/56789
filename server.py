from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import socket

private_file = 'server_private_key.pem'
public_file = 'server_public_key.pem'
allowed = []


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    with open(private_file, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(public_file, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


def privetkluch():
    with open(private_file, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    return private_key


def loadpublic(public_key_file):
    with open(public_key_file, 'rb') as f:
        public_key = load_pem_public_key(f.read())
    return public_key


def encrypt_message(public_key, message):
    encrypted_message = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_message


def decrypt_message(private_key, encrypted_message):
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message.decode('utf-8')


def server():
    generate_keys()

    private_key = privetkluch()


    for i in range(2):
        allowed.append(loadpublic(f'client_public_key_{i}.pem'))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5)

    while True:
        client_socket, addr = server_socket.accept()

        data = client_socket.recv(1024)

        received_public_key = load_pem_public_key(data)

        if received_public_key not in allowed:
            print("Недопустимый публичный ключ. Соединение разорвано.")
            client_socket.close()
        else:
            print("Публичный ключ допустим. Продолжение работы.")

        client_socket.close()


server()
