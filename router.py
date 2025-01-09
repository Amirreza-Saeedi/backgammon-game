import socket
import threading
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from crypto import decrypt_message, encrypt_message
import os

R1_PORT = 60_001
R2_PORT = 60_002
R3_PORT = 60_003
S_PORT = 10_000
IP = '127.0.0.1'

# Router class
class Router:
    '''
        good for r2, r3
        but not r1
    '''

    server_thread = None
    client_thread = None
    s_conn = None
    c_conn = None

    def __init__(self, port, next_port, key):
        self.port = port
        self.next_port = next_port
        self.key = key

    # server -> client
    def listen_to_server(self):    
        while True:
            msg = self.s_conn.recv(1024).decode()
            print('\tSERVER')
            print('msg:', msg)
            en_msg = encrypt_message(self.key, msg)
            self.c_conn.sendall(en_msg.encode())
        pass

    # client -> server
    def listen_to_client(self):
        while True:
            msg = self.c_conn.recv(1024).decode()
            print('\tCLIENT')
            print('msg:', msg)
            de_msg = decrypt_message(self.key, msg)
            self.s_conn.sendall(de_msg.encode())
        pass


    def connect_to_server(self):
        self.s_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_conn.connect((IP, self.next_port))
        self.server_thread = threading.Thread(target=self.listen_to_server)
        self.server_thread.start()

    def accept_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", self.port))
            s.listen()
            
            print(f"Router {self.port} listening...")
            while True:
                try:
                    self.c_conn, addr = s.accept()
                    print(f"Router {self.port} connected to {addr}")
                    # threading.Thread(target=self.listen_to_client, daemon=True).start()
                    self.client_thread = threading.Thread(target=self.listen_to_client)
                    self.client_thread.start()
                except Exception as e:
                    print(f"Router {self.port} error: {e}")
                    pass

    def start(self):
        os.system('cls')

        # connect to server
        self.connect_to_server()

        # accept client
        self.accept_client()

