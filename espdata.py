# This file is part of the Project Name.
# 
# (c) 2024 Sascha420
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
import socket
from datetime import datetime
from zoneinfo import ZoneInfo
from access_conroll import access_door
from cryptography.fernet import Fernet
import os
import cryptography

def decrypt_data(fernet_key_encoded):
    key_fernet_path = os.path.join(os.path.dirname(__file__), "fernet_key.pem")
    fernet_key = open(key_fernet_path, "rb").read().strip()
    fernet = Fernet(fernet_key)
    farnet_key_decrypted = fernet.decrypt(fernet_key_encoded.encode()).decode()
    return farnet_key_decrypted

#def verify_challange(challange_raw, challange_encrypted):
    key_path = os.path.join(os.path.dirname(__file__), "challange_fernet_key.pem")
    fernet_key = open(key_path, "rb").read().strip()
    fernet = Fernet(fernet_key)
    try:
        challange_decrypted = fernet.decrypt(challange_encrypted.encode()).decode()
        return challange_raw == challange_decrypted
    except cryptography.fernet.InvalidToken:
        print("Ungültiges Token: Entschlüsselung fehlgeschlagen")
        return False

def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))  # Binde an alle Schnittstellen auf Port 12345
    server_socket.listen(1)
    print("TCP-Server läuft und wartet auf Verbindungen...")

    while True:
        verify = False
        client_socket, addr = server_socket.accept()
        print(f"Verbindung von {addr} akzeptiert")
        data = client_socket.recv(1024).decode('utf-8')
        data_list = data.split(',')
        rfid_uid = data_list[0]
        fernet_key_encoded = data_list[1]
        challenge_raw = data_list[2]
        challenge_encrypted = data_list[3]
        fernet_key = decrypt_data(fernet_key_encoded)
        if True: #verify_challange(challenge_raw, challenge_encrypted):
            verify = True
            if verify:
                access_door(rfid_uid, fernet_key)
            else:
                print("Challange konnte nicht verifiziert werden")
        
        
        print(f"Getrennte Daten: {data_list}")
        client_socket.close()

# Starte den TCP-Server in einem separaten Thread oder füge ihn in die Hauptschleife ein

