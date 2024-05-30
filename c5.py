import pickle
import socket
from algoritm import DiffHel, Coder

IP = '127.0.0.1'
PORT = 6666

def main():
    sock = socket.socket()
    sock.connect((IP, PORT))

    p = 12
    g = 99
    a = 1

    diff_hel = DiffHel(ab=a, p=p, g=g)
    A = diff_hel.calculate_key


    with open("client_public_key.txt", "w") as file:
        file.write(str(A))

    sock.send(pickle.dumps((p, g, A)))

    try:
        B = pickle.loads(sock.recv(4096))
    except EOFError:
        print("Сервер не ответил. Соединение разорвано.")
        sock.close()
        return

    K = diff_hel.calculate_k(B)
    coder = Coder(K)

    message = input("Введите сообщение: ")
    encrypted_message = coder.code(message)
    sock.send(pickle.dumps(encrypted_message.encode()))

    answer = sock.recv(4096).decode()
    decrypted_answer = coder.decode(answer)
    print("Ответ от сервера = ", decrypted_answer)
    sock.close()

main()
