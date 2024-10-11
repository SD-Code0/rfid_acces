# This file is part of the Project Name.
# 
# (c) 2024 Sascha420
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
import requests
from db_manager import get_user_by_rfid,log_access
import time
import base64
import os
import threading

def default_screen():
    time.sleep(10)
    default_image_path = os.path.join(os.path.dirname(__file__), 'default.png')
    with open(default_image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    url = 'http://localhost:5000/update_ui'
    response = requests.post(url, json={
        'username': "",
        'role': "",
        'image_data': encoded_image,
        'status': 'Geschlossen'
    })
    if response.status_code == 200:
        print("Standard daten an die Web-UI übergeben")
    else:
        print(f"Fehler bei der Anfrage: {response.status_code}")

def open_door():
    print("Tür geöffnet")
    time.sleep(10)

def access_door(rfid_uid,fernet_key):
    
    user = get_user_by_rfid(rfid_uid,fernet_key)
    if user and len(user) >= 4:
        print(f"Zugang gewährt für {user[1]}")
        
        url = 'http://localhost:5000/update_ui'
        response = requests.post(url, json={
            'username': user[1].decode("utf-8"),
            'role': user[2].decode("utf-8"),
            'image_data': user[3],
            'status': 'Success'
        })
        threading.Thread(target=open_door, daemon=True).start()
        log_access(user[0])
        if response.status_code == 200:
            print("Benutzerdaten erfolgreich an die Web-UI übergeben")
            threading.Thread(target=default_screen, daemon=True).start()
        else:
            print(f"Fehler bei der Anfrage: {response.status_code}")


    else:
        print("Zugang verweigert oder unvollständige Benutzerdaten")
        url = 'http://localhost:5000/update_ui'
        response = requests.post(url, json={
            'status': 'Zugang verweigert'
        })
        if response.status_code == 200:
            threading.Thread(target=default_screen, daemon=True).start()