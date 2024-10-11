# This file is part of the Project Name.
# 
# (c) 2024 Sascha420
# 
# This source file is subject to the MIT license that is bundled
# with this source code in the file LICENSE.
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from cryptography.fernet import Fernet


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
                if (data.role) {
                    document.getElementById('Rolle').innerText = 'Rolle: ' + data.role;
                    document.getElementById('Rolle').classList.remove('hidden');
                } else {
                    document.getElementById('Rolle').classList.add('hidden');
                }
                if (data.image_data) {
                    document.getElementById('image').src = 'data:image/jpeg;base64,' + data.image_data;
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
                        if (data.role) {
                            document.getElementById('Rolle').innerText = 'Rolle: ' + data.role;
                            document.getElementById('Rolle').classList.remove('hidden');
                        } else {
                            document.getElementById('Rolle').classList.add('hidden');
                        }
                        if (data.image_data) {
                            document.getElementById('image').src = 'data:image/jpeg;base64,' + data.image_data;
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
            <p id="Rolle" class="hidden">Rolle: </p>
        </div>
    </body>
    </html>
    '''

@app.route('/update_ui', methods=['POST'])
def update_ui():
    global user_data
    data = request.get_json()
    if not data:
       return jsonify({'error': 'Invalid input'}), 403
   
    required_fields = ['username', 'role', 'image_data', 'status']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Invalid input: Missing {field}'}), 403
    
    user_data = {
        'username': data['username'],
        'role': data['role'],
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

    socketio.run(app, host='0.0.0.0', port=5000, debug=True)