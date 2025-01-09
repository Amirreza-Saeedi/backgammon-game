from router import Router
import router as rt
import socket
import threading
from crypto import encrypt_message, decrypt_message

KEY = b"thisisakey123456"

class Router1(Router):

    connections = {}  # (ip, port): conn

    def __init__(self, key):
        super().__init__(key)

    def listen_to_server(self, ip, port):
        '''
            - send msg to proper client
        '''

        # find connection
        while True:
            msg = self.s_conn.recv(1024).decode()
            print('\tSERVER')
            print('msg:', msg)
            en_msg = encrypt_message(self.key, msg)
            '''
                cmd addr data
            '''
            addr
            '''
                ('ip', 1123)
            '''

            self.c_conn.sendall(en_msg.encode())
        

        # send

        pass

    def listen_to_client(self):
        '''

        '''

        '''
            cmd addr msg
        '''
        pass

    def accept_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", self.port))
            s.listen()
            
            print(f"Router {self.port} listening...")
            while True:
                try:
                    c_conn, addr = s.accept()
                    self.connections[addr] = c_conn
                    print(f"Router {self.port} connected to {addr}")
                    threading.Thread(target=self.listen_to_client, daemon=True).start()

                    # send client port to client

                    
                except Exception as e:
                    print(f"Router {self.port} error: {e}")
                    pass
    

if __name__ == '__main__':
    router = Router1(rt.R1_PORT, rt.R2_PORT, KEY)
    router.start()
    
