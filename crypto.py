from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# Utility functions for encryption and decryption
def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return base64.b64encode(nonce + ciphertext).decode()

def decrypt_message(key, encrypted_message):
    data = base64.b64decode(encrypted_message.encode())
    nonce = data[:16]
    ciphertext = data[16:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(ciphertext).decode()