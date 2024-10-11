# This file is part of the Project Name.
# 
# (c) 2024 Sascha420
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
from werkzeug.security import generate_password_hash
import sqlite3
import os

def get_db_connection():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'user.db'))
    cursor = conn.cursor()
    return conn, cursor

def create_tables():
    conn, cursor = get_db_connection()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            passwort TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL 
        )
    ''')
    conn.commit()
    conn.close()

def add_user():
    create_tables()
    conn, cursor = get_db_connection()
    username = input('Enter username: ')
    hashed_password = generate_password_hash(input('Enter password: '))
    role = input('Enter role: ')
    cursor.execute("INSERT INTO users (username, passwort, role) VALUES (?, ?, ?)",
                    (username, hashed_password, role))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_user()