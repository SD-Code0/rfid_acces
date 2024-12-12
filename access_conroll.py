# This file is part of the Project RFID Access contoll .
# 
# (c) 2024 SD-Code0
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
import requests
from db_manager import get_user_by_rfid,log_access,get_devices
import time
import base64
import os
import threading

def default_screen():
    time.sleep(10)
    default_image_path = os.path.join(os.path.dirname(__file__), 'default.png')
    with open(default_image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    url = 'http://127.0.0.1:5002/update_ui'
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

def open_door(device_data):
    
    for device in device_data:
        actor_domain = (device['actor_domain'])
        service = (device['service'])
        entity_id = (device['entity_id'])
    print(f"Öffne Tür mit {actor_domain}.{service} für {entity_id}")
    control_actor(actor_domain, service, entity_id)

def denie_access():
    print("Zugang verweigert oder unvollständige Benutzerdaten")
    default_image_path = os.path.join(os.path.dirname(__file__), 'default.png')
    with open(default_image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    url = 'http://127.0.0.1:5002/update_ui'
    response = requests.post(url, json={
        'username': "",
        'role': "",
        'image_data': encoded_image,
        'status': 'Zugang verweigert'
        })
    if response.status_code == 200:
        threading.Thread(target=default_screen, daemon=True).start()

def access_door(rfid_uid,fernet_key,position):
    device_data = get_devices(position)
    
    user = get_user_by_rfid(rfid_uid,fernet_key)

    
    
    if user and len(user) >= 4:
        for device in device_data:
            device_pos = (device['device_position'])
        if position == str(device_pos):
        
            
            print(f"Zugang gewährt für {user[1]}")
            url = 'http://127.0.0.1:5002/update_ui'
            response = requests.post(url, json={
                'username': user[1].decode("utf-8"),
                'role': user[2].decode("utf-8"),
                'image_data': user[3].decode("utf-8"),
                'status': 'Success'
            })
            threading.Thread(target=open_door(device_data), daemon=True).start()
            log_access(user[0],device_pos)
            if response.status_code == 200:
                print("Benutzerdaten erfolgreich an die Web-UI übergeben")
                threading.Thread(target=default_screen, daemon=True).start()
            else:
                print(f"Fehler bei der Anfrage: {response.status_code}")



    else:
        denie_access()


BASE_URL = "http://homeassistant.local:8123"  
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxZGNlNTUxMjdmZGM0YzBmYmM0YjgyM2FiY2Q2OTBlYyIsImlhdCI6MTczMjMyMzM0MiwiZXhwIjoyMDQ3NjgzMzQyfQ.vKm4hbQ1wTKg1M9KtNsH2Yco5nkqdDxGE5ZsjpU9HpM"  # Ersetze mit deinem Token

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


data = {
    "name": "Testartikel4",
}


def control_actor(domain, service, entity_id):
    """
    Steuert einen Aktor über die Home Assistant API.
    :param domain: Gerätetyp, z. B. 'light', 'switch'
    :param service: Dienst, z. B. 'turn_on', 'turn_off'
    :param entity_id: Entity-ID des Geräts
    :param additional_data: Zusätzliche Daten für den Dienst
    """
    url = f"{BASE_URL}/api/services/{domain}/{service}"
    payload = {
        "entity_id": entity_id
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            print(f"{domain}.{service} erfolgreich ausgeführt für {entity_id}!")
        else:
            print(f"Fehler: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        
def get_status(entity_id):
    url = f"{BASE_URL}/api/states/{entity_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print(f"Aktueller Status von {entity_id}: {data['state']}")
            return data
        else:
            print(f"Fehler: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
    return None