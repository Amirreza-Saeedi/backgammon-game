import socket
import threading
import random
import pickle
import rsa  # Library for RSA encryption and decryption
import os
import commands as cmd
import time


HOST = '127.0.0.1'
PORT = 10_000

players = []  # [name, (ip, port)]
connections = {}  # sockets
lock = threading.Lock()

def tostr_players():
    s = 'Players:\n'
    for i, p in enumerate(players):
        s += f'\t{i + 1}- {p[0]}: {p[1]}\n'
    return s

# Server-side functions
def handle_player(conn, addr):
    global players
    player_name = None

    ### functions
    def handle_request():
        _, target_name, ip, port = data.split()
        print('-----DATA:', data)
        
        # find target player
        with lock:
            target_player = next((p for p in players if p[0] == target_name), None)
            print('--------FOUND')

        if target_player:
            # conn.sendall(f"REQUEST_SENT {target_name}".encode())

            time.sleep(3)  # TODO let connection be created

            target_conn = connections[target_player[1]]
            target_conn.sendall(f"{cmd.REQUEST} {player_name} {ip} {port}".encode())
            
            response = target_conn.recv(1024).decode()
            response = cmd.ACCEPT  # TODO

            if response == cmd.ACCEPT:
                conn.sendall(f"{cmd.ACCEPT} YES {target_player[1]}".encode())
                # target_conn.sendall(f"CONNECTED {addr}".encode())
            else:
                conn.sendall(f"{cmd.ACCEPT} NO {target_player[1]}".encode())


    ### main
    try:
        # Step 1: Add player to the list and share the list
        player_name = conn.recv(1024).decode()
        conn.sendall(str(addr[1]).encode())
        with lock:
            connections[addr] = conn
            players.append((player_name, addr))
        
        print(f"{player_name} connected from {addr}")

        # listen
        while True:
            # Step 2: Receive player requests
            data = conn.recv(1024).decode()

            if data.startswith(cmd.REQUEST):
                print('------REQUEST')
                handle_request()

            # TODO
            elif data.startswith(cmd.CHECK):
                result = random.choice([True, False])
                conn.sendall(f"WIN_STATUS {result}".encode())

            elif data == cmd.DISCONNECT:
                print(f"{player_name} disconnected.")

            elif data == cmd.LIST:
                conn.sendall((cmd.LIST + ' ' + tostr_players()).encode())
                

    except Exception as e:
        print(f"Error handling player {addr}: {e}")

    finally:
        conn.close()
        with lock:
            players = [(name, address) for name, address in players if address != addr]

    



# Server main loop
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_player, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server_socket.close()


if __name__ == '__main__':
    os.system('cls')
    print('\tSERVER APP')
    start_server()
    