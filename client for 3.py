from cryptography.hazmat.primitives import serialization, padding, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def generate_key_pair():
    # Генерация пары ключей (приватный и публичный)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Сериализация ключей в формат PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem, public_pem


# Создание клиентов с разными ключами
client1_private_key, client1_public_key = generate_key_pair()
client2_private_key, client2_public_key = generate_key_pair()

# использование ключей для шифрования и дешифрования сообщений
message = b"Hello, World!"


def encrypt_message(public_key, message):
    # Загрузка публичного ключа из PEM-формата
    loaded_public_key = serialization.load_pem_public_key(
        public_key,
        backend=default_backend()
    )

    # Шифрование сообщения с использованием публичного ключа
    encrypted_message = loaded_public_key.encrypt(
        message, padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_message


def decrypt_message(private_key, encrypted_message):
    # Загрузка приватного ключа из PEM-формата
    loaded_private_key = serialization.load_pem_private_key(
        private_key,
        password=None,
        backend=default_backend()
    )

    # Дешифрование сообщения с использованием приватного ключа
    decrypted_message = loaded_private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted_message


# Шифрование сообщения от клиента 1 для клиента 2
encrypted_message = encrypt_message(client2_public_key, message)

# Дешифрование сообщения клиентом 2
decrypted_message = decrypt_message(client2_private_key, encrypted_message)

print("Decrypted message:", decrypted_message.decode())
