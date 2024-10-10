from cryptography.fernet import Fernet
import cryptography
import os

fernet_key = open("fernet_key.pem", "rb").read()
fernet = Fernet(fernet_key)

data = "123"

enc_data = fernet.encrypt(data.encode())

with open("Encrypted_data.pem", "wb") as f:
    f.write(enc_data)