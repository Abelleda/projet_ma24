import socket
import time
import mysql.connector

mydb = None
mycursor = None

class db:
    def connect():
        global mydb, mycursor
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="casino"
            )

            if mydb.is_connected():
                print("Connected to MySQL database")
                mycursor = mydb.cursor()
                return True

        except:
            print("Couldnt connect to MySQL database")
            return False

class functions:
    def get_user_data(username):
        mycursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        result = mycursor.fetchall()
        return {
            "id": result[0][0],
            "username": result[0][1],
            "password": result[0][2],
            "balance": result[0][3],
            "date_created": result[0][4]
        }

    def user_exist(username):
        mycursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        result = mycursor.fetchall()
        if result:
            return True
        
        return False

    def login(username: str, password: str):
        print(username, password)
        if functions.user_exist(username):
            user_data = functions.get_user_data(username)
            if user_data["password"] == password:
                globals.user.id = user_data["id"]
                globals.user.username = user_data["username"]
                globals.user.password = user_data["password"]
                globals.user.balance = user_data["balance"]
                globals.user.date_created = user_data["date_created"]
                return True
        
        return False

    def register(username: str, password: str):
        try:
            mycursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password,))
            mydb.commit()

            return True
        except:
            return False

class Game:
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
    db.connect()
    print(functions.get_user_data("awd"))

    try:
        while True:
            # Optional: you could periodically check DB or do tasks here
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        print("Exiting program...")