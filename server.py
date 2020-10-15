import socket
import threading

HOST = '127.0.0.1'
PORT = 8080
ADDR = (HOST, PORT)
BUF_SIZE = 1024
FORMAT = 'utf-8'

class Server(threading.Thread):
    """
    Crea un servidor capac de rebre diferents clients
    """

    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        """
        Metode que s'executa quan es crida el metode start() de la classe
        Thread. 
        
        Aquest metode crea el nou socket i l'enllaca amb la IP i 
        el port del servidor.
        """
        
        # Creem el nou socket del servidor
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Establim la IP i el port del servidor
            s.bind(ADDR)
            print('[STARTING] Starting the server')

            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Habilitem que el servidor accepti connexions externes
            s.listen()
            print(f'[LISTENING] Server listening on {ADDR}...')
            
            while True:
                # Restem a l'espera d'acceptar qualsevol connexio
                clientSocket, address = s.accept()

                # Creem un nou socket a traves de la crida del client que es vol 
                # connectar al nostre servidor
                connection = Connection(clientSocket, address, self)
                connection.start()

                # Afegim aquesta nova connexio a la llista de connexions actives
                self.connections.append(connection)

    def broadcast(self, message, source):
        """
        Envia el missatge passat per parametre a totes les
        adreces menys la que tambe es passa per paramtre. 

        Aixo es aixi perque l'adreca que es passa es la del client
        que envia el missatge
        """
        for c in self.connections:
            if c.address != source:
                c.send(message)

    def removeConnection(self, connection):
        """
        Elimina una connexio de la llista de connexions.
        """
        self.connections.remove(connection)


class Connection(threading.Thread):
    """
    Crea la connexio entre el client i el servidor
    """

    def __init__(self, socket, address, server):
        super().__init__()
        self.socket = socket
        self.address = address
        self.server = server

    def run(self):
        """
        Metode que s'executa quan es crida el metode start() de la classe
        Thread. 
        
        Aquest metode rep el missatge que s'envia pel socket i el gestiona
        per saber despres si l'ha d'enviar o ha de tancar la connexio
        """
        while True:
            # Obtenim el missatge i el convertim de Bytes a String
            message = self.socket.recv(BUF_SIZE).decode(FORMAT)

            # Mirem si el missatge no esta buit
            if message:
                # Enviem el missatge a tots els altres clients que estiguin connectats
                self.server.broadcast(message, self.address)
            # Si esta buit vol dir que s'ha tancat la connexio
            else:
                # Tanquem el socket
                self.socket.close()

                # Treiem el socket de la llista de connexions
                self.server.removeConnection(self)

                # Borrem el socket
                return

    def send(self, message: str):
        """
        Envia el missatge a traves del socket
        """
        self.socket.sendall(message.encode(FORMAT))


def exit(server):
    """
    Elimina totes les connexions que hi ha dins del servidor
    """
    while True:
        # Obtenim el missatge que entra el client
        inputMessage = input('')

        # Mirem si el missatge es igual a '>q'
        if inputMessage == '>q':
            # Tanquem totes les connexions del servidor
            for c in server.connections:
                c.socket.close()

if __name__ == "__main__":
    # Creem el servidor i l'executem
    server = Server(HOST, PORT)
    server.start()

    # Creem un fil per executar el metode 'exit'
    threadExit = threading.Thread(target=exit, args=(server,))
    threadExit.start()
