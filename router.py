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

    def __init__(self, port, next_port):
        self.port = port
        self.next_port = next_port

    # server -> client
    def listen_to_server(self, s_conn, c_conn, key):
        while True:
            msg = s_conn.recv(1024).decode()
            print('\tSERVER')
            print('msg:', msg)
            en_msg = encrypt_message(key, msg)
            c_conn.sendall(en_msg.encode())

    # client -> server
    def listen_to_client(self, c_conn, s_conn, key):

        '''
            first recv keys in 3 msg
            msgs are non-crypted keys:
            1- key1
            2- key2 
            3- key3
        '''
        # # set key
        # msg = str(c_conn.recv(1024).decode())
        # print('key:', msg)
        # self.key = msg.encode()  # TODO encode or not?

        # main loop
        while True:
            msg = c_conn.recv(1024).decode()
            print('\tCLIENT')
            print('msg:', msg)
            print("*** ", key)
            de_msg = decrypt_message(key, msg)
            s_conn.sendall(de_msg.encode())

    def handle_client(self, c_conn):

        # set key
        msg = c_conn.recv(1024).decode()  # Receive raw bytes
        keys = msg.split(' ')
        print('key:', msg)
        # key = msg.encode()  # TODO encode or not?
        if self.port == R1_PORT:
            key = keys[0].encode()
            s_conn = self.connect_to_server(c_conn=c_conn, key=key)
            s_conn.sendall(msg.encode())
            print('----', key)
        elif self.port == R2_PORT:
            key = keys[1].encode()
            s_conn = self.connect_to_server(c_conn=c_conn, key=key)
            s_conn.sendall(msg.encode())
            print('----', key)
        elif self.port == R3_PORT:
            key = keys[2].encode()
            s_conn = self.connect_to_server(c_conn=c_conn, key=key)
            print('----', key)

        # listen to client
        self.listen_to_client(c_conn=c_conn, s_conn=s_conn, key=key)

    def connect_to_server(self, c_conn, key):
        s_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_conn.connect((IP, self.next_port))
        threading.Thread(target=self.listen_to_server, daemon=True, args=(s_conn, c_conn, key)).start()
        return s_conn

    def accept_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", self.port))
            s.listen()

            print(f"Router {self.port} listening...")
            while True:
                try:
                    conn, addr = s.accept()
                    print(f"Router {self.port} connected to {addr}")
                    threading.Thread(target=self.handle_client, daemon=True, args=(conn,)).start()
                except Exception as e:
                    print(f"Router {self.port} error: {e}")
                    pass

    def start(self):
        os.system('cls')
        # accept client
        self.accept_client()

