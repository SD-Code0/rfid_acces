# This file is part of the Project RFID Access contoll .
# 
# (c) 2024 SD-Code0
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
            position TEXT NOT NULL,
            access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) 
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices(
            device_id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_domain TEXT NOT NULL,
            service TEXT NOT NULL,
            entity_id TEXT NOT NULL UNIQUE,
            device_position TEXT NOT NULL
        )
    ''')
    
    
    conn.commit()
    conn.close()

def add_user(username, rfid_uid, role, image_path=None):
    conn, cursor = get_db_connection()
    try:
        
        fernet_key = Fernet.generate_key()
        fernet = Fernet(fernet_key)
        
        if image_path:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            default_image_path = os.path.join(os.path.dirname(__file__), 'default.png')
            with open(default_image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                
        encrypted_image = fernet.encrypt(encoded_image.encode())
                                                   


        
        global_fernet = Fernet(open("fernet_key.pem", "rb").read())  
        
        encrypted_fernetkey = global_fernet.encrypt(fernet_key)
        print("Fernetkey-add-user: ") #debug
        print(encrypted_fernetkey)
        encrypted_username = fernet.encrypt(username.encode())
        #encrypted_role = fernet.encrypt(role.encode())
        cursor.execute("INSERT INTO users (username, rfid_uid, role, image) VALUES (?, ?, ?, ?)",
                    (encrypted_username, rfid_uid, role, encrypted_image))
        conn.commit()
        return "success" , encrypted_fernetkey.decode("utf-8")

    except sqlite3.IntegrityError:
        print("RFID ist bereits vorhanden.")
    except FileNotFoundError:
        print("Default image file not found.")
    finally:
        conn.close()

def delete_user_by_rfid(rfid_uid):
    conn, cursor = get_db_connection()
    cursor.execute("DELETE FROM users WHERE rfid_uid = ?", (rfid_uid,))
    conn.commit()
    print(f"User mit rfid {rfid_uid} wurde gelöscht.")
    conn.close()

def get_users():
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id, rfid_uid, role FROM users")
    users = cursor.fetchall()
    conn.close()

    user_list = []
    for user in users:
        # Falls role Bytes enthält, vorher als UTF-8 decodieren (oder Base64)
        role_data = user[2]
        if isinstance(role_data, bytes):
            role_data = role_data.decode("utf-8", errors="replace")

        user_dict = {
            'id': role_data,     # "role" landet hier als "id"
            'rfid_uid': user[1]
        }
        user_list.append(user_dict)

    return user_list
    

def get_user_by_rfid(rfid_uid, fernet_key):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id, username, role, image FROM users WHERE rfid_uid = ?", (rfid_uid,))
    user = cursor.fetchone()


    if user is None:
        conn.close()
        return None

    user_id, enc_username, enc_role, enc_image = user

    fernet = Fernet(fernet_key)
    username = fernet.decrypt(enc_username)
    role = enc_role
    image_dec = fernet.decrypt(enc_image)

    user = (user_id, username, role, image_dec)
    print(user)
    conn.close()
    return user

def get_access_logs(date):
    conn, cursor = get_db_connection()
    cursor.execute('''
        SELECT access_logs.log_id, access_logs.user_id, users.rfid_uid, access_logs.access_time, access_logs.position
        FROM access_logs
        JOIN users ON access_logs.user_id = users.id
        WHERE DATE(access_logs.access_time) = ?
    ''', (date,))
    logs = cursor.fetchall()
    conn.close()
    log_list = []
    for log in logs:
        log_dict = {
            'timestamp': log[3],
            'log_entry': log[0],
            'user_id': log[1],
            'rfid_uid': log[2],
            'position': log[4]
        }
        log_list.append(log_dict)
    
    return log_list
 
 
def user_exists_by_rfid(rfid):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT id FROM users WHERE rfid_uid = ?", (rfid,))
    user = cursor.fetchone()
    conn.close()
    return user is not None   

def db_check_entity_id(entity_id):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT EXISTS(SELECT 1 FROM devices WHERE entity_id = ?)", (entity_id,))
    exists = cursor.fetchone()[0]
    conn.close()
    return bool(exists)

def get_devices(location):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT device_id, actor_domain, service, entity_id, device_position FROM devices WHERE device_position = ?",(location,))
    devices = cursor.fetchall()
    conn.close()
    
    device_list = []
    for device in devices:
        device_dict = {
            'device_id': device[0],
            'actor_domain': device[1],
            'service': device[2],
            'entity_id': device[3],
            'device_position': device[4]
        }
        device_list.append(device_dict)
    
    return device_list

def db_add_device(actor_domain, service, entity_id, device_position):
    conn, cursor = get_db_connection()
    cursor.execute("""
        INSERT INTO devices (actor_domain, service, entity_id, device_position)
        VALUES (?, ?, ?, ?)
    """, (actor_domain, service, entity_id, device_position))
    conn.commit()
    conn.close()

def db_delete_device(position):
    conn, cursor = get_db_connection()
    try:
        cursor.execute("DELETE FROM devices WHERE device_position = ?", (position,))
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError("Kein Gerät zum Löschen gefunden.")
    finally:
        conn.close()

def device_exists(position):
    conn, cursor = get_db_connection()
    cursor.execute("SELECT COUNT(*) FROM devices WHERE device_position = ?", (position,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def get_devices_by_pos():   
    conn,cursor = get_db_connection()
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()
    conn.close()
    return devices

def delete_logs_from_db(date):
    conn, cursor = get_db_connection()
    cursor.execute("DELETE FROM access_logs WHERE DATE(access_time) = ?", (date,))
    conn.commit()
    conn.close()

def log_access(user_roll, position):
    conn, cursor = get_db_connection()
    cursor.execute("INSERT INTO access_logs (user_id,position) VALUES (?,?)", (user_roll,position))
    conn.commit()
    conn.close()
def save_data_to_db(data):
    conn, cursor = get_db_connection()
    conn.commit()
    conn.close()
    
#Testing admin gen

def create_admin_user_table_if_not_exists():
    conn, cursor = get_db_connection()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            passwort TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()
