import sqlite3

def init_db():
    with sqlite3.connect('license_server.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                license_type TEXT NOT NULL,
                serial_key TEXT NOT NULL UNIQUE,
                max_users INTEGER NOT NULL,
                current_users INTEGER NOT NULL DEFAULT 0
            )
        ''')
        conn.commit()


from flask import Flask, request, jsonify
import sqlite3
import time
import threading

app = Flask(__name__)
db_lock = threading.Lock()


@app.route('/generate_license', methods=['POST'])
def generate_license():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    license_type = data.get('license_type')

    max_users = 10 if license_type == 'small' else 50
    serial_key = f"{username[:3]}{license_type[:1]}{int(time.time()) % 1000000}"

    with db_lock, sqlite3.connect('license_server.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO licenses (username, password, license_type, serial_key, max_users) VALUES (?, ?, ?, ?, ?)',
            (username, password, license_type, serial_key, max_users)
        )
        conn.commit()
    return jsonify({"serial_key": serial_key, "max_users": max_users})


@app.route('/verify_license', methods=['POST'])
def verify_license():
    serial_key = request.json.get('serial_key')
    with db_lock, sqlite3.connect('license_server.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT max_users, current_users FROM licenses WHERE serial_key = ?', (serial_key,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"status": "error", "message": "Invalid serial key"}), 400

        max_users, current_users = result
        if current_users < max_users:
            cursor.execute('UPDATE licenses SET current_users = current_users + 1 WHERE serial_key = ?', (serial_key,))
            conn.commit()
            return jsonify({"status": "success", "message": "Authorized"})
        else:
            return jsonify({"status": "error", "message": "License limit reached"}), 403


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    serial_key = request.json.get('serial_key')
    # 保留空逻辑
    return jsonify({"status": "success"})

def heartbeat_checker():
    while True:
        # TODO: 实现逻辑，超时处理
        time.sleep(30)

if __name__ == '__main__':
    init_db()
    threading.Thread(target=heartbeat_checker, daemon=True).start()
    app.run(debug=True)