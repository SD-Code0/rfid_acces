# This file is part of the Project Name.
# 
# (c) 2024 Sascha420
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
import sqlite3
import os
import base64
from cryptography.fernet import Fernet

def get_db_connection():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'rfid_access_control.db'))
    cursor = conn.cursor()
    return conn, cursor

def create_tables():
    conn, cursor = get_db_connection()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            rfid_uid TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            image TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs(
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) 
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, rfid_uid, role, image_path=None):
    conn, cursor = get_db_connection()
    try:
        if image_path:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            default_image_path = os.path.join(os.path.dirname(__file__), 'default.png')
            with open(default_image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        fernet_key = Fernet.generate_key()
        
        fernet = Fernet(fernet_key)
        with open(f"{username}_fernet_key.pem", "wb") as f:
            f.write(fernet_key)
        
        encrypted_username = fernet.encrypt(username.encode())
        encrypted_role = fernet.encrypt(role.encode())
        cursor.execute("INSERT INTO users (username, rfid_uid, role, image) VALUES (?, ?, ?, ?)",
                    (encrypted_username, rfid_uid, encrypted_role, encoded_image))
        conn.commit()
    except sqlite3.IntegrityError:
        print("RFID ist bereits vorhanden.")
    except FileNotFoundError:
        print("Default image file not found.")
    finally:
        conn.close()

def delete_user(rfid_uid):
    conn, cursor = get_db_connection()
    cursor.execute("DELETE FROM users WHERE rfid_uid = ?", (rfid_uid,))
    conn.commit()
    print(f"User mit rfid {rfid_uid} wurde gelöscht.")
    conn.close()

def get_users():
    conn, cursor = get_db_connection()
    print("gerade mit verschlüsselten Daten")
    cursor.execute("SELECT id, username, rfid_uid, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_by_rfid(rfid_uid, fernet_key):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id, username, role, image FROM users WHERE rfid_uid = ?", (rfid_uid,))
    user = cursor.fetchone()
    user_id = user[0]
    username = user[1]
    role = user[2]
    image = user[3]
    fernet = Fernet(fernet_key)
    username = fernet.decrypt(username)
    role = fernet.decrypt(role)
    user = (user_id, username, role, image)
    conn.close()
    return user

def get_access_logs(date):
    conn, cursor = get_db_connection()
    cursor.execute('''
        SELECT access_logs.log_id, access_logs.user_id, users.username, users.role, access_logs.access_time
        FROM access_logs
        JOIN users ON access_logs.user_id = users.id
        WHERE DATE(access_logs.access_time) = ?
    ''', (date,))
    logs = cursor.fetchall()
    conn.close()
    return logs

def check_rfids(rfid_uid):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT rfid_uid FROM users WHERE rfid_uid = ?", (rfid_uid,))
    rfid = cursor.fetchone()
    conn.close()
    return rfid

def delete_all_logs():
    conn, cursor = get_db_connection()
    cursor.execute("DELETE FROM access_logs")
    conn.commit()
    print("Alle Einträge in access_logs wurden gelöscht.")
    conn.close()

def log_access(user_id):
    conn, cursor = get_db_connection()
    cursor.execute("INSERT INTO access_logs (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()