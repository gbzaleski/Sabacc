import socket
import pickle

class Network:
    def __init__(self, _server, _port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = _server
        self.port = _port
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def get_p(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))
        except socket.error as err:
            print("Error: ", err)

