from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)

# Временное хранилище пользователей
users = {}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "Пользователь уже существует!", 400
        hashed_password = generate_password_hash(password)
        users[username] = {
            'password': hashed_password,
            'registration_date': datetime.datetime.utcnow().isoformat()
        }
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            return redirect(url_for('dashboard', username=username))
        return "Неправильное имя пользователя или пароль!", 400
    return render_template('login.html')


@app.route('/dashboard/<username>')
def dashboard(username):
    user = users.get(username)
    if user:
        return render_template('dashboard.html', username=username, registration_date=user['registration_date'])
    return "Пользователь не найден!", 404


@app.route('/api/user/', methods=['POST'])
def api_register():
    data = request.json
    username = data['username']
    password = data['password']
    if username in users:
        return jsonify({'error': 'Пользователь уже существует!'}), 400
    hashed_password = generate_password_hash(password)
    users[username] = {
        'password': hashed_password,
        'registration_date': datetime.datetime.utcnow().isoformat()
    }
    return jsonify({'message': 'Пользователь успешно зарегистрирован!'}), 201


if __name__ == '__main__':
    app.run(debug=True)
