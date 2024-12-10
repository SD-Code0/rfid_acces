# This file is part of the Project RFID Access contoll .
# 
# (c) 2024 Sascha420
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
from flask import Flask, request, render_template, redirect, url_for, jsonify, session, flash
from werkzeug.security import check_password_hash
from flask_socketio import SocketIO
from flask_cors import CORS
import os
import threading
import web_ui
import signal
import sqlite3
from espdata import start_tcp_server
from web_ui import mainpage
from db_manager import add_user,delete_user_by_rfid,get_users,get_access_logs,delete_logs_from_db,create_tables,get_devices_by_pos,db_add_device
create_tables()



def run_webui():
    web_ui.socketio.run(web_ui.app,host='0.0.0.0', port=5002, debug=False)



webui_thread = threading.Thread(target=run_webui, daemon = True)
webui_thread.start()

tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
tcp_thread.start()

mainpage()

def shutdown_server():
    os.kill(os.getpid(), signal.SIGINT)




app = Flask(__name__)
app.secret_key = os.urandom(24)  
socketio = SocketIO(app)
CORS(app)


users = []
logs = []

def get_user_db_connection():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'user.db'))
    cursor = conn.cursor()
    return conn, cursor

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn, cursor = get_user_db_connection()
        
        in_username = request.form['username']
        in_password = request.form['password']
        
        cursor.execute("SELECT id, username, passwort, role FROM users WHERE username = ?", (in_username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[2], in_password):
            session['logged_in'] = True
            return redirect(url_for('homepage'))
        else:
            flash('Ungültiger Benutzername oder Passwort')
    return render_template('homepage.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/add_user', methods=['POST'])
def add_user_route():
    if 'logged_in' in session:
        data = request.get_json()
        username = data.get('username')
        rfid = data.get('rfid')
        role = data.get('role')
        file = data.get('file')
        
        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
        else:
            file_path = None
        
        add_user(username, rfid, role, file_path)
        return jsonify({"status": "success", "username": username, "rfid": rfid, "role": role})
    else:
        return redirect(url_for('login'))

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'logged_in' in session:
        data = request.get_json()
        rfid_uid = data.get('rfid')
        if rfid_uid:
            delete_user_by_rfid(rfid_uid)
            return jsonify({"status": "success", "rfid": rfid_uid})
        else:
            return jsonify({"status": "error", "message": "No RFID provided"})
        
    else:
        return redirect(url_for('login'))

@app.route('/show_users', methods=['GET'])
def show_users():
    if 'logged_in' in session:
        users = get_users()
        
        users.sort(key=lambda user: user['id'])
        return jsonify(users)
    else:
        return redirect(url_for('login'))

@app.route('/get_logs', methods=['POST'])
def get_logs():
    if 'logged_in' in session:
        log_date = request.form['log_date']
        logs = get_access_logs(log_date)
        return jsonify(logs)
    else:
        return redirect(url_for('login'))

@app.route('/delete_logs', methods=['POST'])
def delete_logs():
    if 'logged_in' in session:
        log_date = request.form['log_date']
        delete_logs_from_db(log_date)
        return jsonify({"status": "success", "message": f"Logs for {log_date} deleted"})
    else:
        return redirect(url_for('login'))

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if 'logged_in' in session:
        shutdown_server()
        return 'Server shutting down...'
    else:
        return redirect(url_for('login'))



@app.route('/add_device', methods=['POST'])
def add_device():
    actor_domain = request.form.get('actor_domain')
    service = request.form.get('service')
    entity_id = request.form.get('entity_id')
    device_position = request.form.get('device_position')

    if not all([actor_domain, service, entity_id, device_position]):
        return jsonify({'status': 'error', 'message': 'Alle Felder sind erforderlich'}), 400
    else:
        db_add_device(actor_domain, service, entity_id, device_position)
        return jsonify({'status': 'success', 'message': 'Gerät hinzugefügt'})

@app.route('/get_devices', methods=['GET'])
def get_devices():
    try:
        devices = get_devices_by_pos()

        # Debug-Ausgabe
        print("Abgerufene Geräte:", devices)

        devices_list = [
            {
                'device_id': device[0],
                'actor_domain': device[1],
                'service': device[2],
                'entity_id': device[3],
                'device_position': device[4]
            } for device in devices
        ]
        return jsonify(devices_list)
    except Exception as e:
        print("Fehler beim Abrufen der Geräte:", str(e))  # Debug
        return jsonify({'status': 'error', 'message': str(e)}), 500
if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5001, debug=False)