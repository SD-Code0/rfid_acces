# This file is part of the Project RFID Access contoll .
# 
# (c) 2024 Sascha420
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
import socket
from access_conroll import access_door,denie_access
from cryptography.fernet import Fernet
import os


def verify_challange(challange_raw, challange_encrypted):
    fernet_key = open("challange_fernet_key.pem", "rb").read()
    fernet = Fernet(fernet_key)
    challange_decrypted = fernet.decrypt(challange_encrypted.encode()).decode()
    if challange_raw == challange_decrypted:
        return True
    else:
        return False
    

def decrypt_data(fernet_key_encoded):
    if fernet_key_encoded:
        key_fernet_path = os.path.join(os.path.dirname(__file__), "fernet_key.pem")
        fernet_key = open(key_fernet_path, "rb").read().strip()
        fernet = Fernet(fernet_key)
        farnet_key_decrypted = fernet.decrypt(fernet_key_encoded.encode()).decode()
        return farnet_key_decrypted
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
            position = data_list[2]
            #print(f"RFID: {rfid_uid}, Fernetkey: {fernet_key_encoded}, Position: {position}")
            fernet_key = decrypt_data(fernet_key_encoded)
            print(f"rfid_uid: {rfid_uid}, fernet_key: {fernet_key}, position: {position}")
            access_door(rfid_uid, fernet_key, position)
        #if data_list and len(data_list) >= 4:
        #    rfid_uid = data_list[0]
        #    fernet_key_encoded = data_list[1]
        #    challenge_raw = data_list[2]
        #    challenge_encrypted = data_list[3]
        #    position = data_list[4]
        #    fernet_key = decrypt_data(fernet_key_encoded)
        #    if verify_challange(challenge_raw, challenge_encrypted):
        #        access_door(rfid_uid, fernet_key, position)
        #    else:
        #        print("Challange konnte nicht verifiziert werden")
        else:
            denie_access()
            print("ungültige Daten erhalten")
            print(f"die ehaltenden daten sind: {data_list}")
        
        
        
        client_socket.close()


