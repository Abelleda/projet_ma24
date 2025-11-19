import socket

cards = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,

    "J": 10,
    "Q": 10,
    "K": 10,

    "A": 1 or 11
}

class DataBase:
    pass

class BlackJack:
    clients = {}

    def server_start():
        host = socket.gethostname()
        port = 5000

        server_socket = socket.socket()
        server_socket.bind((host, port))
        server_socket.listen()

        while True:
            conn, addr = server_socket.accept()
            print("Connection from: " + str(addr))

            #username = 

        conn.close()


if __name__ == '__main__':
    BlackJack.server_program()