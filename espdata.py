# This file is part of the Project RFID Access contoll .
# 
# (c) 2024 SD-Code0
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
import socket

from access_conroll import access_door,denie_access
from cryptography.fernet import Fernet
import os
import base64

def verify_challange(challange_raw, challange_encrypted):
    fernet_key = open("challange_fernet_key.pem", "rb").read()
    fernet = Fernet(fernet_key)
    challange_decrypted = fernet.decrypt(challange_encrypted.encode()).decode()
    if challange_raw == challange_decrypted:
        return True
    else:
        return False
    

def fix_padding(encoded_data):
    missing_padding = len(encoded_data) % 4
    if missing_padding:
        encoded_data += '=' * (4 - missing_padding)
    return encoded_data



def decrypt_data(fernet_key_encoded):
    if fernet_key_encoded:
        fernet_key_encoded = fix_padding(fernet_key_encoded)
        key_fernet_path = os.path.join(os.path.dirname(__file__), "fernet_key.pem")
        fernet_key = open(key_fernet_path, "rb").read().strip()
        fernet = Fernet(fernet_key)
        fernet_key_decrypted = fernet.decrypt(fernet_key_encoded.encode())
        return fernet_key_decrypted
    else:
        print("Kein Fernetkey bekommen")


def start_tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))  # Binde an alle Schnittstellen auf Port 12345
    server_socket.listen(1)
    print("TCP-Server läuft und wartet auf Verbindungen...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Verbindung von {addr} akzeptiert")
        data = client_socket.recv(1024).decode('utf-8')
        data_list = data.split(',')
        if data_list and len(data_list) >= 3:
            rfid_uid = data_list[0]
            fernet_key_encoded = data_list[1]
            print(fernet_key_encoded)
            position = data_list[2]
            fernet_key = decrypt_data(fernet_key_encoded)
            print(f"rfid_uid: {rfid_uid}, fernet_key: {fernet_key_encoded}, position: {position}")
            access_door(rfid_uid, fernet_key, position)
        else:
            denie_access()
            print("ungültige Daten erhalten")
            print(f"die ehaltenden daten sind: {data_list}")
     
        
        
        client_socket.close()

def start_tcp_server_port2():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12346))
    server_socket.listen(5)
    print("TCP-Server 2 läuft und wartet auf Verbindungen...")

    stored_rfid = "NO_RFID"
    stored_enc_key = None

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Verbindung von {addr} akzeptiert")
        data = client_socket.recv(1024).decode('utf-8').strip()

        if data == "GET_RFID":
            # RFID zurücksenden
            client_socket.sendall(stored_rfid.encode('utf-8'))

        elif data == "GET_FERNET":
            # Fernet-Key zurücksenden, falls vorhanden
            if stored_enc_key is not None:
                response = "ENC:" + stored_enc_key
                client_socket.sendall(response.encode('utf-8'))
            else:
                client_socket.sendall(b"NO_KEY")
        elif data == "ERFOLG":
            stored_enc_key = None
            print("Erfolg erhalten")

        elif data.startswith("ENC:"):
            # Fernet-Key speichern
            stored_enc_key = data[4:]
            print(f"Fernet-Key erhalten und gespeichert: {stored_enc_key}")
            client_socket.sendall(b"Fernet-Key erhalten")

        elif data.startswith("RFID:"):
            # RFID aktualisieren
            stored_rfid = data[5:]
            print(f"RFID aktualisiert: {stored_rfid}")
            client_socket.sendall(b"RFID gesetzt")

        else:
            # Unbekannter Befehl
            print("Unbekannter Befehl erhalten:", data)
            client_socket.sendall(b"Unbekannter Befehl")

        client_socket.close()

