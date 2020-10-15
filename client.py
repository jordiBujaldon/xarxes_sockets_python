import os
import socket
import threading

HOST = '127.0.0.1'
PORT = 8080
ADDR = (HOST, PORT)
BUF_SIZE = 1024
FORMAT = 'utf-8'


class Send(threading.Thread):

    def __init__(self, socket, name):
        super().__init__()
        self.socket = socket
        self.name = name

    def run(self):
        while True:
            message = input(f'{self.name}: ')

            if message == 'QUIT':
                break
            else:
                self.socket.sendall ('{}: {}'.format(self.name, message).encode(FORMAT))            
        self.socket.close()
        os._exit(0)


class Receive(threading.Thread):

    def __init__(self, socket, name):
        super().__init__()
        self.socket = socket
        self.name = name

    def run(self):    
        while True:
            message = self.socket.recv(BUF_SIZE)

            if message:
                print(f'\r{message.decode(FORMAT)}\n{self.name}: ', end='')
            else:
                print('ERROR, the server has lost!')            
                print('Quitting...')
                self.socket.close()
                os._exit(0)


class Client():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def start(self):
        self.socket.connect((self.host, self.port))

        name = input('Introdueix el teu nom: ')

        send = Send(self.socket, name)
        receive = Receive(self.socket, name)

        send.start()
        receive.start()

if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.start()