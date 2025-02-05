# This file is part of the Project Name.
# 
# (c) 2024 SD-Code0
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from cryptography.fernet import Fernet
import requests
import base64
import os

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

user_data = None



@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Access UI</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #000000;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                background-color: #fff;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                text-align: center;
            }
            .hidden {
                display: none;
            }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
        <script>
            var socket = io();
            socket.on('update_data', function(data) {
                if (data.username) {
                    document.getElementById('Username').innerText = 'Username: ' + data.username;
                    document.getElementById('Username').classList.remove('hidden');
                } else {
                    document.getElementById('Username').classList.add('hidden');
                }
                if (data.user_uid) {
                    document.getElementById('User-ID').innerText = 'User-ID: ' + data.user_uid;
                    document.getElementById('User-ID').classList.remove('hidden');
                } else {
                    document.getElementById('User-ID').classList.add('hidden');
                }
                if (data.image_data) {
                    document.getElementById('image').src = 'data:image/png;base64,' + data.image_data;
                }
                if (data.status) {
                    document.getElementById('Status').innerText = data.status;
                }
            });
            window.onload = function() {
                fetch('/get_user_data')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        if (data.username) {
                            document.getElementById('Username').innerText = 'Username: ' + data.username;
                            document.getElementById('Username').classList.remove('hidden');
                        } else {
                            document.getElementById('Username').classList.add('hidden');
                        }
                        if (data.user_uid) {
                            document.getElementById('User-ID').innerText = 'User-ID: ' + data.user_uid;
                            document.getElementById('User-ID').classList.remove('hidden');
                        } else {
                            document.getElementById('User-ID').classList.add('hidden');
                        }
                        if (data.image_data) {
                            document.getElementById('image').src = 'data:image/png;base64,' + data.image_data;
                        }
                        if (data.status) {
                            document.getElementById('Status').innerText = data.status;
                        }
                    }
                });
            };
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Tür zugang</h1>
            <img id="image" src="default.png" alt="Image" width="200">
            <p>Status: <span id="Status">Geschlossen</span></p>
            <p id="Username" class="hidden">Username: </p>
            <p id="User-ID" class="hidden">User-ID: </p>
        </div>
    </body>
    </html>
    '''

def mainpage():
    default_image_path = os.path.join(os.path.dirname(__file__), 'default.png')
    with open(default_image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    url = 'http://127.0.0.1:5002/update_ui'
    response = requests.post(url, json={
        'username': "",
        'user_uid': "",
        'image_data': encoded_image,
        'status': 'Geschlossen'
        })

@app.route('/update_ui', methods=['POST'])
def update_ui():
    global user_data
    data = request.get_json()
    if not data:
       return jsonify({'error': 'Invalid input'}), 403
   
    required_fields = ['username', 'user_uid', 'image_data', 'status']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Invalid input: Missing {field}'}), 403
    
    user_data = {
        'username': data['username'],
        'user_uid': data['user_uid'],
        'image_data': data['image_data'],
        'status': data['status']
    }

    socketio.emit('update_data', user_data)
    return jsonify({'status': 'success'})

@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    global user_data
    if user_data:
        return jsonify(user_data)
    else:
        return jsonify({'error': 'Keine Benutzerdaten vorhanden'})

if __name__ == '__main__':

    socketio.run(app, host='0.0.0.0', port=5002, debug=False)