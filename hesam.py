import socket
import threading
import time
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

# Router class
class Router:
    def __init__(self, port, next_port, key):
        self.port = port
        self.next_port = next_port
        self.key = key

    def handle_client(self, conn):
        data = conn.recv(1024).decode()
        print(f"Router {self.port} received: {data}")
        decrypted_data = decrypt_message(self.key, data)

        if self.next_port:
            # Send to the next router
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", self.next_port))
                s.sendall(decrypted_data.encode())
                response = s.recv(1024)
            encrypted_response = encrypt_message(self.key, response.decode())
            conn.sendall(encrypted_response.encode())
        else:
            # Final destination (server)
            response = f"Server processed: {decrypted_data}"
            encrypted_response = encrypt_message(self.key, response)
            conn.sendall(encrypted_response.encode())

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", self.port))
            s.listen()
            print(f"Router {self.port} listening...")
            while True:
                conn, _ = s.accept()
                threading.Thread(target=self.handle_client, args=(conn,)).start()

# Client class
class Client:
    def __init__(self, router_port, keys):
        self.router_port = router_port
        self.keys = keys

    def send_message(self, message):
        encrypted_message = message
        for key in reversed(self.keys):
            encrypted_message = encrypt_message(key, encrypted_message)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", self.router_port))
            s.sendall(encrypted_message.encode())
            response = s.recv(1024).decode()

        decrypted_response = response
        for key in self.keys:
            decrypted_response = decrypt_message(key, decrypted_response)

        print(f"Client received: {decrypted_response}")

# Start routers
def start_router(port, next_port=None, key=None):
    router = Router(port, next_port, key)
    router.start()

# Main execution
if __name__ == "__main__":
    keys = [get_random_bytes(16) for _ in range(3)]  # Three random keys for encryption layers
    time.sleep(1)  # Allow time for routers to start

    # Start routers in separate threads, passing the correct keys to each router
    threading.Thread(target=start_router, args=(5000, 5001, keys[0]), daemon=True).start()
    threading.Thread(target=start_router, args=(5001, 5002, keys[1]), daemon=True).start()
    threading.Thread(target=start_router, args=(5002, None, keys[2]), daemon=True).start()

    # Start the client
    client = Client(5000, keys)
    client.send_message("Hello, Server!")
