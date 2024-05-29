from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer

def main():
    # Создан экземпляр фиктивного авторизатора для управления "виртуальными" пользователями
    authorizer = DummyAuthorizer()

    # Определен новый пользователь с полными правами доступа к r/w и домашним каталогом
    authorizer.add_user("user", "12345", "/home/user", perm="elradfmw")

    # Создан экземпляр класса обработчика TLS FTP
    handler = TLS_FTPHandler
    handler.certfile = "server.crt.txt"
    handler.keyfile = "server_private_key.pem"
    handler.authorizer = authorizer

    # Определен безопасный контекст с помощью протокола SSL
    handler.tls_control_required = True
    handler.tls_data_required = True

    # Создан экземпляр класса FTP-сервера и прослушан в 0.0.0.0:21
    address = ("0.0.0.0", 21)
    server = FTPServer(address, handler)

    # Start serving
    server.serve_forever()

if __name__ == "__main__":
    main()

