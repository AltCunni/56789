import os
import shutil
import socket
import logging
import sqlite3

HOST = 'localhost'
PORT = 9090
ROOT_DIR = 'restricted_folder'
DB_FILE = 'users.db'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'adminpass'

logging.basicConfig(filename='server_log.txt', level=logging.INFO)


def create_user_table():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL UNIQUE,
                 password TEXT NOT NULL,
                 folder TEXT NOT NULL,
                 quota INTEGER NOT NULL)''')

    conn.commit()
    conn.close()



def register_user(username, password, quota):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    folder = os.path.join(ROOT_DIR, username)
    os.mkdir(folder)

    c.execute("INSERT INTO users (username, password, folder, quota) VALUES (?, ?, ?, ?)",
              (username, password, folder, quota))

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


# Другие функции остаются без изменений

def process_admin_command(command):
    parts = command.split(' ')
    if parts[0] == 'list_users':
        return list_users()
    elif parts[0] == 'set_quota':
        username = parts[1]
        quota = int(parts[2])
        return set_quota(username, quota)
    else:
        return "Неверная команда для администратора"


def list_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT username, quota FROM users")
    users = c.fetchall()

    conn.close()

    user_list = '\\n'.join([f"{user[0]} - Квота: {user[1]} МБ" for user in users])
    return user_list


def set_quota(username, quota):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("UPDATE users SET quota=? WHERE username=?", (quota, username))
    conn.commit()
    conn.close()

    return f"Квота для пользователя '{username}' успешно установлена: {quota} МБ"


def start_server():
    create_user_table()

    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen()

    while True:
        conn, addr = sock.accept()

        request = conn.recv(1024).decode()

        if request.startswith('register'):
            _, username, password, quota = request.split(' ')
            register_user(username, password, int(quota))
            response = f"Пользователь '{username}' успешно зарегистрирован."
        else:
            if request.startswith('admin_login'):
                _, username, password, command = request.split(' ')
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    response = process_admin_command(command)
                else:
                    response = "Ошибка аутентификации администратора."
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