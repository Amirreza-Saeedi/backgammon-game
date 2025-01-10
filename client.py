import socket
import threading
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

from backgammon import my_id
from crypto import decrypt_message, encrypt_message
import commands as cmd
import os
import router as rt
from player import Player
import backgammon as bg

HOST = '127.0.0.1'
PORT = rt.R1_PORT

game_thread = None
conn = None
p2p_socket = None
op_addr = None
p2p_conn = None
player = None

# generate keys
KEYS = [get_random_bytes(16) for _ in range(3)]
KEYS[0] = b'1234123412341234'
KEYS[1] = b'abcdabcdabcdabcd'
KEYS[2] = b'!@#$!@#$!@#$!@#$'

def start_game():
    pass

def send_to_server(conn, msg: str):
    '''
        encrypt and send
    '''
    # encrypt
    for key in reversed(KEYS):
        msg = encrypt_message(key, msg.strip())
    # send
    conn.sendall(msg.encode())

def send_to_p2p(conn, msg: str):
    '''
        encode and send
    '''
    conn.sendall(msg.strip().encode())

def recv_from_server(conn):
    msg = str(conn.recv(1024).decode())
    # decrypt
    for key in KEYS:
        msg = decrypt_message(key, msg)
    # ret
    return msg

def listen_to_server(conn):  # TODO should handle more tasks
    '''
        - list of players
        - request
        - roll dice
    '''
    global p2p_conn
    global player
    global game_thread
    def print_server():
        print('S: ' + msg)

    while True:
        try:
            msg = recv_from_server(conn)

            if msg.startswith(cmd.LIST):
                print('\n\tLIST')
                print_server()  # show player list

            elif msg.startswith(cmd.REQUEST):
                print('\n\tREQUEST RECV')
                # conncet to p2p socket
                _, name, ip, port = msg.split()  # opponent info
                print_server()
                # response = input('Do you accept? (y): ')
                response = cmd.ACCEPT  # TODO
                send_to_server(conn, response)

                # connect to client
                p2p_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                p2p_conn.connect((ip, int(port)))

                p2p_thread = threading.Thread(target=listen_to_p2p, daemon=True)
                p2p_thread.start()

                game_thread = threading.Thread(target=run_game, daemon=True, args=[1,])
                game_thread.start()
                player.id = 1

                print('Connected to player', name, ip, port)

            elif msg.startswith(cmd.ACCEPT):
                print('\n\tACCEPT')
                print_server()

            # cmd d1 d2
            elif msg.startswith(cmd.ROLL):
                print('\n\tROLL')
                print_server()
                _, d1, d2 = msg.split()
                d1 = int(d1)
                d2 = int(d2)
                # TODO set dices in game
                bg.roll_dice(d1, d2)

            #cmd true/False
            elif msg.startswith(cmd.CHECK):
                print('\n\tCHECK')
                print()
                result = msg.split()[1]
                if result == my_id:
                    print("You Won.")
                    bg.show_winner(bg.game.window, my_id + 1, bg.game)
                elif result == (my_id +1) % 2:
                    print("You Dicked also op won.")
                    if my_id ==0:
                        bg.show_winner(bg.game.window, 1, bg.game)
                    else:
                        bg.show_winner(bg.game.window, 2, bg.game)
                    #من شام
                #TODO

        except Exception as e:
            print("Connection cs closed by server.", e)
            break


def listen_to_p2p():
    '''
        - chat
        - move
    '''
    global p2p_conn
    global conn
    while True:
        try:
            msg = str(p2p_conn.recv(1024).decode())


            if msg.startswith(cmd.CHAT):
                print('\n\tCHAT')
                print('<<<', msg)

            elif msg.startswith(cmd.MOVE):
                print('\n\tMOVE')
                print(msg)
                _, player_id, column_taken, column_pus = msg.split()
                print('----before')
                print('game', bg.game)
                bg.game.update_board(int(player_id), int(column_taken), int(column_pus))
                print('----after')

            elif msg.startswith(cmd.CHECK):
                print('\n\tCHECK')
                p1 = bg.game.stats[0][1]
                p2 = bg.game.stats[1][1]
                send_to_server(conn, cmd.CHECK + ' ' + str(p1) + ' ' + str(p2))
            else:
                print('Error: Unknown p2p command.')

        except Exception as e:
            print("Connection p2p closed.", e)
            break
    pass

def connect_to_server():
    global conn
    # connect
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((HOST, PORT))
    print('Connected to server.')

    # send keys
    # TODO .encode() or not
    # TODO chat way

    conn.sendall(KEYS[0])
    print('Key 1 set.')

    en_key2 = encrypt_message(KEYS[0], KEYS[1].decode())
    conn.sendall(en_key2.encode())
    print('Key 2 set.')

    en_key3 = encrypt_message(KEYS[1], KEYS[2].decode())
    en_key3 = encrypt_message(KEYS[0], en_key3)
    conn.sendall(en_key3.encode())
    print('Key 3 set.')

    # server thread
    threading.Thread(target=listen_to_server, daemon=True, args=[conn]).start()

    return conn

def run_game(my_id):
    global p2p_conn
    if p2p_conn:
        bg.main(p2p_conn, my_id, conn)
    else:
        print('Error: No p2p connection')

def handle_commands(conn):
    global player
    global p2p_conn
    global game_thread

    while True:
        command = input("~ Enter command (list/request/chat/check/disconnect): ")

        ### server commands
        # request <name>
        if command.startswith('request'):
            print('\tREQUEST SEND')
            _, target_name = command.split()
            # cmd op_name p_ip p_port
            send_to_server(conn, f"{cmd.REQUEST} {target_name} {HOST} {player.port}")  # TODO id instead of name

            p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            p2p_socket.bind((HOST, player.port))
            p2p_socket.listen()
            print(f"Client listening on {HOST}:{player.port}")

            print('Waiting 10 seconds for accept...')
            s_time = time.time()
            e_time = 0

            try:
                while e_time < 10:
                    e_time = time.time() - s_time
                    p2p_conn, op_addr = p2p_socket.accept()
                    print(f"Connection accepted from {op_addr}")
                    p2p_thread = threading.Thread(target=listen_to_p2p, daemon=True)
                    p2p_thread.start()

                    game_thread = threading.Thread(target=run_game, daemon=True, args=[0,])
                    game_thread.start()
                    player.id = 0

                    break

                if e_time > 10:
                    print("No connection happend.")
                    p2p_socket.close()

            except KeyboardInterrupt:  # TODO tmp for accept()
                print("Shutting down server...")
            except Exception as e:
                print(f'Error in request {e}')


        elif command.startswith('check'):
            p1 = bg.game.stats[0][1]
            p2 = bg.game.stats[1][1]
            send_to_p2p(p2p_conn,cmd.CHECK)
            send_to_server(conn, cmd.CHECK + ' ' +  str(p1) + ' ' + str(p2))

        elif command == 'disconnect':
            send_to_server(conn, cmd.DISCONNECT)
            break

        elif command == 'list':
            send_to_server(conn, cmd.LIST)

        elif command == 'roll':
            send_to_server(conn, cmd.ROLL)

        ### p2p commands
        elif command == 'chat':  # p2p
            print('\tCHAT')
            if p2p_conn:
                txt = input('>>> ')
                send_to_server(p2p_conn, cmd.CHAT + ' ' + player.name + ': ' + txt)
            else:
                print('Error: no p2p connection.')
            # p2p_conn.sendall(cmd.CHAT.encode())
            pass

        ### offline commands
        # elif command == 'play':
        #     run_game(player.id)

        else:
            print("Unknown command.")

def greet_server(conn):
    global player

    # init player
    name = input("Enter your player name: ")  # TODO to main
    port = int(input('Enter port number: '))
    player = Player(name=name, port=port)

    # name id port
    send_to_server(conn, player.name + ' ' + HOST + ' ' + str(player.port)) 


def client_program():

    conn = connect_to_server()

    greet_server(conn)

    handle_commands(conn)

    conn.close()

if __name__ == '__main__':
    os.system('cls')
    print('\tCLIENT APP')
    client_program()

