import socket

HOST = 'localhost'
PORT = 9090


def send_command(command):
    sock = socket.socket()
    sock.connect((HOST, PORT))

    sock.send(command.encode())

    response = sock.recv(1024).decode()
    print(response)

    sock.close()


while True:
    command = input('Kitty: ')

    send_command(command)

    if command == 'exit':
        break
