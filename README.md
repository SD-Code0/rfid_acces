# RFID Access

## 1. Project Description
This project is an RFID access control system that uses technologies such as Python, SQLite, Flask, and Arduino. It enables user management, access rights management, and logs access events.

## 2. Installation

### 2.1 Clone the Repository
```sh
git clone https://github.com/SD-Code0/rfid_acces.git
cd rfid_acces
```

### 2.2 Install Dependencies
```sh
python3 -m venv rfid_venv
source rfid_venv/bin/activate
pip install -r requirements.txt
```

### 2.3 Upload the Arduino Sketch
Open the file `RFIDauslesung.ino` in the Arduino IDE.

#### Configuration
- **WiFi Settings**:  
  Edit the file `ESP32_RFIDauslesung.ino` and add your WiFi SSID and password:
  ```c++
  const char* ssid = "your-ssid";
  const char* password = "your-password";
  const char* host = "your-server-ip";
  ```
  
Upload the sketch to your ESP32.

## 3. Usage

### 3.1 Start the Application
```sh
source rfid_venv/bin/activate
python3 main.py
```
The Web UI is available at your server’s IP address on port `5001`, for example:
```sh
192.168.188.2:5001
```
When you first load the Web UI, you will be prompted to create an admin account required for future access.

### 3.2 Add Devices
Open the Web UI and go to **Devices** → **Add Device**. Enter all required information.

### 3.3 Add Users
Open the Web UI and go to **User Management** → **Add User**. Enter all required data. The RFID can be read with the write station.

### 3.4 Delete Users
Open the Web UI and go to **User Management** → **Delete User**. Either enter the RFID tag manually or place it on the write station and click **Read RFID**.

## 4. License
This project is licensed under the MIT License. See the LICENSE file for details.

## 5. Third-Party Libraries
- **SQLite**  
  License: Public Domain  
  Link: [SQLite License](https://www.sqlite.org/copyright.html)

- **Flask**  
  License: BSD-3-Clause  
  Link: [Flask License](https://github.com/pallets/flask/blob/main/LICENSE.rst)

- **cryptography**  
  License: Apache License 2.0  
  Link: [cryptography License](https://github.com/pyca/cryptography/blob/main/LICENSE)


