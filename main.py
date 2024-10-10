# This file is part of the Project Name.
# 
# (c) 2024 Sascha420
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.

from flask import Flask
import threading
from db_manager import create_tables, add_user, delete_user, get_users, get_access_logs, delete_all_logs
import web_ui
from access_conroll import access_door
from datetime import datetime
from zoneinfo import ZoneInfo
from espdata import start_tcp_server
create_tables()

def run_webui():
    web_ui.socketio.run(web_ui.app, debug=False)

webui_thread = threading.Thread(target=run_webui)
webui_thread.daemon = True
webui_thread.start()
tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
tcp_thread.start()

while True:
    print("\nWas möchtest du tun? \n 1: Benutzer hinzufügen \n 2: Benutzer löschen \n 3: Alle Benutzer anzeigen \n 4: Tür Öffnung  \n 5: Zugriffsprotokolle anzeigen \n 6: Lösche alle Zugriffsprotokolle \n 0: Beenden")

    choice = input("Wähle eine Option: ")

    if choice == "1":
        username = input("Username: ")
        rfid_uid = input("RFID_UID: ")
        role = input("Role: ")
        image_path = input("Bildpfad (optional): ")
        if username and rfid_uid and role:
            add_user(username, rfid_uid, role, image_path)
        else:
            print("Eine der Angaben ist unvollständig")

    elif choice == "2":
        rfid_uid = input("RFID_UID: ")
        delete_user(rfid_uid)

    elif choice == "3":
        users = get_users()
        if users:
            for user in users:
                print(user)
        else:
            print("Keine Benutzer vorhanden.")

    elif choice == "4":
        rfid_uid = input("RFID_UID: ")
        access_door(rfid_uid)

    elif choice == "5":
        date_choice = input("Möchtest du die heutigen Logs sehen? (y/n): ")
        if date_choice.lower() == "y":
            tz = ZoneInfo('Europe/Berlin')
            current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
            print(f"Aktuelles Datum und Uhrzeit in MEZ: {current_time}")
            date = datetime.now(tz).date().strftime("%Y-%m-%d")
            
        else:
            date = input("Datum (YYYY-MM-DD): ")
        logs = get_access_logs(date)
        if logs:
            for log in logs:
                log_id, user_id, username, role, access_time = log
                access_time = datetime.fromisoformat(access_time).replace(tzinfo=ZoneInfo('UTC')).astimezone(tz)
                print(f"Log ID: {log_id}, UserID: {user_id}, Benutzer: {username}, Rolle: {role}, Zugriff um: {access_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    elif choice == "6":
        delete = input("Möchtest du wirklich alle Logs löschen? (y/n): ")
        if delete.lower() == "y":
            delete_all_logs()

    elif choice == "0":
        print("Programm beendet.")
        break
    else:
        print("Ungültige Auswahl.")