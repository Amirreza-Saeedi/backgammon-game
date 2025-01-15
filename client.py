import socket
import threading
import time
from math import trunc

import string
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from tkinter import Tk, messagebox
from crypto import decrypt_message, encrypt_message
import commands as cmd
import os
import router as rt
from player import Player
import backgammon as bg
import easygui
import random

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
# KEYS[0] = b'1234123412341234'
# KEYS[1] = b'abcdabcdabcdabcd'
# KEYS[2] = b'!@#$!@#$!@#$!@#$'



def create_random_keys():
    # Define the character pool: lowercase letters and digits 1-9
    char_pool = string.ascii_lowercase + '123456789'
    
    # Generate a list of 3 random strings, each 16 characters long
    keys = [(''.join(random.choices(char_pool, k=16))).encode() for _ in range(3)]
    return keys

KEYS = create_random_keys()

def sweet_revenge(text):
    # response = messagebox.askyesno("revenge time", text)
    response = easygui.ynbox(text, title="Confirmation", choices=("Yes", "No"))

    return response

def start_game():
    pass

def send_to_server(conn, msg: str,KEY):
    '''
        encrypt and send
    '''
    # encrypt
    for key in reversed(KEY):
        msg = encrypt_message(key, msg.strip())
    # send
    print("+++ ",KEY)
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
                response = input('Do you accept? (y): ')
                # response = cmd.ACCEPT  # TODO
                if response == 'y':
                    # send_to_server(conn, cmd.ACCEPT)

                    # connect to client
                    p2p_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    p2p_conn.connect((ip, int(port)))

                    p2p_thread = threading.Thread(target=listen_to_p2p, daemon=True)
                    p2p_thread.start()

                    game_thread = threading.Thread(target=run_game, daemon=True, args=[1,])
                    game_thread.start()
                    player.id = 1

                    print('Connected to player', name, ip, port)

            # cmd d1 d2
            elif msg.startswith(cmd.ROLL):
                print('\n\tROLL')
                print_server()
                _, d1, d2 = msg.split()
                d1 = int(d1)
                d2 = int(d2)
                bg.roll_dice(d1, d2)

            #cmd true/False
            elif msg.startswith(cmd.CHECK):
                print('\n\tCHECK')
                print_server()
                result = int(msg.split()[1])

                if result == player.id:
                    print("You Won.")
                    bg.show_winner(bg.game.window, player.id + 1, bg.game)
                    game_thread.join()

                elif result == (player.id +1) % 2:
                    print("You Dicked also op won.")
                    thread = None
                    if player.id == 0:
                        bg.show_winner(bg.game.window, 1, bg.game)
                    else:
                        bg.show_winner(bg.game.window, 2, bg.game)
                    
                    game_thread.join()
                    print('----JOINED')

                    # Display the Yes/No dialog
                    respond = sweet_revenge("Do you want to revenge and rematch?")

                    print('respond', respond)
                    if respond:
                        send_to_p2p(p2p_conn, cmd.REVENGE)
                    else:
                        p2p_conn.close()
                        p2p_conn = None
                        print('-----p2p closed')

        except Exception as e:
            print("Connection cs closed by server.", e)
            break


def listen_to_p2p():
    '''
        - chat
        - move
    '''
    def print_client():
        print('C:', msg)

    global p2p_conn
    global conn
    while True:
        try:
            msg = str(p2p_conn.recv(1024).decode())

            print_client()

            if msg.startswith(cmd.CHAT):
                print('\n\tCHAT')
                print('<<<', msg)

            if msg == cmd.REMOVE:
                print('\n\tREMOVE')
                bg.game[(player.id + 1) % 2][1] += 1

            # cmd id ct cp
            elif msg.startswith(cmd.MOVE):
                print('\n\tMOVE')
                print_client()
                _, player_id, column_taken, column_pus = msg.split()
                bg.game.update_board(int(player_id), int(column_taken), int(column_pus))

            # cmd turn
            elif msg.startswith(cmd.TURN):
                print('\n\tTURN')
                print_client()
                _, nturn = msg.split()
                bg.game.set_turn(int(nturn), both=False)



            elif msg.startswith(cmd.CHECK):
                print('\n\tCHECK')
                p1 = bg.game.stats[0][1]
                p2 = bg.game.stats[1][1]
                send_to_server(conn, cmd.CHECK + ' ' + str(p1) + ' ' + str(p2),KEYS)

            elif msg.startswith(cmd.REVENGE):

                print('\n\tREVENGE')
                respond = sweet_revenge("Do you want rematch?")

                if respond:
                    send_to_p2p(p2p_conn, cmd.REMATCH)
                    threading.Thread(target=run_game, daemon=True,args=(player.id,)).start()
                else:
                    send_to_p2p(p2p_conn,cmd.BREAK)
                    p2p_conn.close()
                    p2p_conn = None
                    break

            elif msg.startswith(cmd.REMATCH):
                print('\n\tREMATCH')
                threading.Thread(target=run_game, daemon=True, args=(player.id,)).start()
            
            elif msg.startswith(cmd.BREAK):
                print("Break excuted")
                break

            else:
                print('Error: Unknown p2p command.')

        except Exception as e:
            print("Connection p2p closed.", e)
            break

def connect_to_server():
    global conn
    # connect
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((HOST, PORT))
    print('Connected to server.')
    # print("---key1= ", KEYS[0])
    # conn.sendall(KEYS[0])
    # print('Key 1 set.')

    # print("---key2= ", KEYS[1])
    # # en_key2 = encrypt_message(KEYS[0], KEYS[1].decode())
    # conn.sendall(KEYS[1])
    # print('Key 2 set.')

    # print("---key3= ", KEYS[2])
    # # en_key3 = encrypt_message(KEYS[1], KEYS[2].decode())
    # # en_key3 = encrypt_message(KEYS[0], en_key3)
    # conn.sendall(KEYS[2])
    # print('Key 3 set.')
    # for i, key in enumerate(KEYS):
    #     print(f"---key{i + 1}= {key}")
    #     conn.sendall(key)  # Send raw bytes
    #     print(f"Key {i + 1} set.")
    #     time.sleep(3)
    msg = KEYS[0].decode()+' '+KEYS[1].decode()+' '+KEYS[2].decode()
    conn.sendall(msg.encode())
    # server thread
    threading.Thread(target=listen_to_server, daemon=True, args=[conn]).start()

    return conn

def run_game(my_id):
    global p2p_conn
    if p2p_conn:
        bg.main(p2p_conn, my_id, conn,KEYS)
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
            _, target_port = command.split()
            # cmd op_name p_ip p_port
            send_to_server(conn, f"{cmd.REQUEST} {target_port} {HOST} {player.port}",KEYS)  # TODO id instead of name

            p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            p2p_socket.bind((HOST, player.port))
            p2p_socket.listen()
            print(f"Client listening on {HOST}:{player.port}")

            print('Waiting 10 seconds for accept...')
            p2p_socket.settimeout(10)

            try:
                p2p_conn, op_addr = p2p_socket.accept()
                print(f"Connection accepted from {op_addr}")
                p2p_thread = threading.Thread(target=listen_to_p2p, daemon=True)
                p2p_thread.start()

                game_thread = threading.Thread(target=run_game, daemon=True, args=[0,])
                game_thread.start()
                player.id = 0

            except KeyboardInterrupt:  # TODO tmp for accept()
                print("Shutting down server...")
            except socket.timeout:
                print("Timeout happend.")
            except Exception as e:
                print(f'Error in request {e}')
            finally:
                p2p_socket.close()


        elif command.startswith('check'):
            p1 = bg.game.stats[0][1]
            p2 = bg.game.stats[1][1]
            send_to_p2p(p2p_conn,cmd.CHECK)
            send_to_server(conn, cmd.CHECK + ' ' +  str(p1) + ' ' + str(p2),KEYS)

        elif command == 'disconnect':
            send_to_server(conn, cmd.DISCONNECT,KEYS)
            break

        elif command == 'list':
            send_to_server(conn, cmd.LIST,KEYS)

        ### p2p commands
        elif command == 'chat':  # p2p
            print('\tCHAT')
            if p2p_conn:
                txt = input('>>> ')
                send_to_p2p(p2p_conn, cmd.CHAT + ' ' + player.name + ': ' + txt)
            else:
                print('Error: no p2p connection.')
            # p2p_conn.sendall(cmd.CHAT.encode())
            pass

        else:
            print("Unknown command.")

def greet_server(conn):
    global player

    # init player
    name = input("Enter your player name: ")  # TODO to main
    port = int(input('Enter port number: '))
    player = Player(name=name, port=port)

    # name id port
    send_to_server(conn, player.name + ' ' + HOST + ' ' + str(player.port),KEYS) 


def client_program():

    conn = connect_to_server()

    greet_server(conn)

    handle_commands(conn)

    conn.close()

if __name__ == '__main__':
    os.system('cls')
    print('\tCLIENT APP')
    client_program()

