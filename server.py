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
    ip, port = None, None

    ### functions
    def handle_request():
        _, target_port, ip, port = data.split()
        target_port = int(target_port)

        # find target player
        print('playesr')
        for p in players:
            print(p[1][1])

        with lock:
            target_player = next((p for p in players if p[1][1] == target_port), None)

        if target_player:
            print('- Pleyer found.')

            time.sleep(3)  # let connection be created

            target_conn = connections[target_player[1]]
            target_conn.sendall(f"{cmd.REQUEST} {player_name} {ip} {port}".encode())

        else:
            print('- Player not found.')

    def print_client():
        print(f'C({player_name}:{port}): ' + data)

    def send_to_client(msg: str):
        conn.sendall(msg.strip().encode())

    ### main
    try:
        # Step 1: Add player to the list and share the list
        print('\tNEW PLAYER')
        player_name, ip, port = str(conn.recv(1024).decode()).split()
        with lock:
            connections[addr] = conn
            players.append((player_name, addr))

        data = f"connected from {addr}"
        print_client()

        ### listen
        while True:
            # Step 2: Receive player requests
            data = str(conn.recv(1024).decode())

            if data.startswith(cmd.REQUEST):
                print('\tREQUEST')
                print_client()
                handle_request()

            elif data.startswith(cmd.CHECK):
                print('\tCHECK')
                print_client()
                p1 = data.split()[1]
                p2 = data.split()[2]

                # TODO test
                p1 = '15'

                if p1 == "15":
                    send_to_client(cmd.CHECK + ' ' + '0')
                elif p2 == "15":
                    send_to_client(cmd.CHECK + ' ' + '1')
                else:
                    send_to_client(cmd.CHECK + ' ' + '-1')

            elif data == cmd.DISCONNECT:
                print('\tDISCONNECT')
                connections.pop(addr)
                idx = players.index((player_name, addr))
                players.pop(idx)
                print_client()
                print(f"- {player_name} disconnected.")

            elif data == cmd.LIST:
                print('\tLIST')
                print_client()
                send_to_client(cmd.LIST + ' ' + tostr_players())

            elif data.startswith(cmd.ROLL):
                print('\tROLL')
                print_client()
                d1 = random.randint(1, 6)
                d2 = random.randint(1, 6)
                send_to_client(cmd.ROLL + ' ' + str(d1) + ' ' + str(d2))



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
            print(f"Server {PORT} connected to router {addr}")
            threading.Thread(target=handle_player, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server_socket.close()


if __name__ == '__main__':
    os.system('cls')
    print('\tSERVER APP')
    start_server()
