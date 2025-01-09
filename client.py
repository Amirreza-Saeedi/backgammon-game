import socket
import threading
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from crypto import decrypt_message, encrypt_message

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

























# HOST = '127.0.0.1'
# PORT = 10_000  # TODO tor 1
# M_PORT = 50_000
#
# server_thread = None
# p2p_thread = None
# playing_thread = None
# p2p_socket = None
# op_addr = None
# p2p_conn = None
#
# def start_game():
#     pass
#
# def listen_to_server(cs_conn):  # TODO should handle more tasks
#     '''
#         - list of players
#         - request
#     '''
#     global p2p_conn
#
#     while True:
#         try:
#             msg = str(cs_conn.recv(1024).decode())
#
#             if msg.startswith(cmd.LIST):
#                 print('\n\tLIST')
#                 print('Server:', msg)  # show player list
#
#             elif msg.startswith(cmd.REQUEST):
#                 print('\n\tREQUEST RECV')
#                 # conncet to p2p socket
#                 _, name, ip, port = msg.split()  # opponent info
#                 print('Server:', msg)
#                 # response = input('Do you accept? (y): ')
#                 response = cmd.ACCEPT  # TODO
#                 cs_conn.sendall(response.encode())
#
#                 p2p_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 p2p_conn.connect((ip, int(port)))
#
#                 p2p_thread = threading.Thread(target=listen_to_p2p, daemon=True)
#                 p2p_thread.start()
#
#                 print('Connected to player', name, ip, port)
#
#                 pass
#
#             elif msg.startswith(cmd.ACCEPT):
#                 print('\n\tACCEPT')
#                 print(msg)
#
#                 pass
#
#
#         except Exception as e:
#             print("Connection closed by server.", e)
#             break
#
#
# def listen_to_p2p():
#     '''
#         - chat
#     '''
#     global p2p_conn
#     while True:
#         try:
#             msg = str(p2p_conn.recv(1024).decode())
#
#
#             if msg.startswith(cmd.CHAT):
#                 print('\n\tCHAT')
#                 print('<<<', msg)
#             else:
#                 print('Error: Unknown p2p command.')
#
#         except Exception as e:
#             print("Connection closed by server.", e)
#             break
#     pass
#
#
# def client_program():
#     global M_PORT
#     global p2p_socket
#     global p2p_conn
#     global op_addr
#
#     cs_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     cs_conn.connect((HOST, PORT))
#
#     player_name = input("Enter your player name: ")  # TODO to main
#     cs_conn.sendall(player_name.encode())
#     # M_PORT = int(cs_conn.recv(1024).decode())
#
#     listening_thread = threading.Thread(target=listen_to_server, daemon=True, args=[cs_conn])
#     listening_thread.start()
#
#     while True:
#         command = input("~ Enter command (list/request/chat/check/disconnect): ")
#
#         ### choices
#
#         if command.startswith('request'):
#             print('\tREQUEST SEND')
#             _, target_name = command.split()
#             cs_conn.sendall(f"{cmd.REQUEST} {target_name} {HOST} {M_PORT}".encode())  # TODO id instead of name
#
#             p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             p2p_socket.bind((HOST, M_PORT))
#             p2p_socket.listen()
#             print(f"Client listening on {HOST}:{M_PORT}")
#
#             print('Waiting 10 seconds for accept...')
#             s_time = time.time()
#             e_time = 0
#
#             try:
#                 while e_time < 10:
#                     e_time = time.time() - s_time
#                     p2p_conn, op_addr = p2p_socket.accept()
#                     print(f"Connection accepted from {op_addr}")
#                     p2p_thread = threading.Thread(target=listen_to_p2p, daemon=True)
#                     p2p_thread.start()
#                     break
#
#                 if e_time > 10:
#                     print("No connection happend.")
#                     p2p_socket.close()
#
#             except KeyboardInterrupt:  # TODO tmp for accept()
#                 print("Shutting down server...")
#
#
#         elif command == 'check':
#             print('\tCHECK')
#             cs_conn.sendall(cmd.CHECK.encode())
#
#         elif command == 'disconnect':
#             print('\tDISCONNECT')
#             cs_conn.sendall(cmd.DISCONNECT.encode())
#             break
#
#         elif command == 'list':
#             print('\tLIST')
#             cs_conn.sendall(cmd.LIST.encode())
#
#         elif command == 'chat':  # p2p
#             print('\tCHAT')
#             if p2p_conn:
#                 txt = input('>>> ')
#                 p2p_conn.sendall((cmd.CHAT + ' ' + player_name + ': ' + txt).strip().encode())
#             else:
#                 print('Error: no p2p connection.')
#             # p2p_conn.sendall(cmd.CHAT.encode())
#             pass
#
#         else:
#             print("Unknown command.")
#
#     cs_conn.close()
#
# if __name__ == '__main__':
#     os.system('cls')
#     print('\tCLIENT APP')
#     client_program()
#
