import os
import shutil
import socket
import logging
import sqlite3

HOST = 'localhost'
PORT = 9090
ROOT_DIR = 'restricted_folder' #все действия пользователя будут ограничены в пределах директории
DB_FILE = 'users.db'

logging.basicConfig(filename='server_log.txt', level=logging.INFO)


def tablesql():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL UNIQUE,
                 password TEXT NOT NULL,
                 folder TEXT NOT NULL)''')

    conn.commit()
    conn.close()


def register_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    folder = os.path.join(ROOT_DIR, username)
    os.mkdir(folder)

    c.execute("INSERT INTO users (username, password, folder) VALUES (?, ?, ?)",
              (username, password, folder))

    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()

    conn.close()

    if user:
        return True, user[3]  # Возвращаем папку пользователя при успешной аутентификации
    else:
        return False, None


def list_files(user_folder):
    files = os.listdir(user_folder)
    return '\\n'.join(files)


def create_folder(user_folder, folder_name):
    os.mkdir(os.path.join(user_folder, folder_name))
    return f"Папка '{folder_name}' успешно создана."


def delete_folder(user_folder, folder_name):
    shutil.rmtree(os.path.join(user_folder, folder_name))
    return f"Папка '{folder_name}' успешно удалена."


def delete_file(user_folder, file_name):
    os.remove(os.path.join(user_folder, file_name))
    return f"Файл '{file_name}' успешно удален."


def rename_file(user_folder, old_name, new_name):
    os.rename(os.path.join(user_folder, old_name), os.path.join(user_folder, new_name))
    return f"Файл '{old_name}' успешно переименован в '{new_name}'."


def copy_file_to_server(user_folder, file_name):
    shutil.copyfile(file_name, os.path.join(user_folder, f'server_{file_name}'))
    return f"Файл '{file_name}' успешно скопирован на сервер."


def copy_file_to_client(user_folder, file_name):
    shutil.copyfile(os.path.join(user_folder, file_name), f'client_{file_name}')
    return f"Файл '{file_name}' успешно скопирован на клиент."


def process_command(command, user_folder):
    parts = command.split(' ')
    if parts[0] == 'list':
        return list_files(user_folder)
    elif parts[0] == 'create_folder':
        folder_name = parts[1]
        return create_folder(user_folder, folder_name)
    elif parts[0] == 'delete_folder':
        folder_name = parts[1]
        return delete_folder(user_folder, folder_name)
    elif parts[0] == 'delete_file':
        file_name = parts[1]
        return delete_file(user_folder, file_name)
    elif parts[0] == 'rename_file':
        old_name = parts[1]
        new_name = parts[2]
        return rename_file(user_folder, old_name, new_name)
    elif parts[0] == 'copy_to_server':
        file_name = parts[1]
        return copy_file_to_server(user_folder, file_name)
    elif parts[0] == 'copy_to_client':
        file_name = parts[1]
        return copy_file_to_client(user_folder, file_name)
    elif parts[0] == 'exit':
        return "Выход"
    else:
        return "Неверная команда"


def start_server():
    tablesql()

    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen()

    while True:
        conn, addr = sock.accept()

        request = conn.recv(1024).decode()
        if request.startswith('register'):
            _, username, password = request.split(' ')
            register_user(username, password)
            response = f"Пользователь '{username}' успешно зарегистрирован."
        else:
            username, password, command = request.split(' ')
            authenticated, user_folder = authenticate_user(username, password)

            if authenticated:
                response = process_command(command, user_folder)
            else:
                response = "Ошибка аутентификации. Проверьте правильность логина и пароля."

        conn.send(response.encode())

        logging.info(f"Адрес: {addr}, Команда: {request}, Ответ: {response}")

        if response == "Выход":
            break

    sock.close()

start_server()