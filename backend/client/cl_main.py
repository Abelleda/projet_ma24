import os
import mysql.connector 
import socket
import time

### Setup ###
mydb = None
mycursor = None
### end Setup ###

class globals:
    max_username_length = 20
    min_password_length = 5
    max_password_length = 30
    class user:
        id = -1
        username = ""
        password = ""
        balance = 0
        date_created = ""

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
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        result = mycursor.fetchall()
        if result:
            return True
        
        return False

    def login(username: str, password: str):
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
        mycursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password,))
        mydb.commit()

        pages.__init__()

class pages:
    def login():
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if functions.login(username, password):
            print(f"Welcome {globals.user.username}!")
            pages.play_blackjack()

    def register():
        username_passed = False
        password_passed = False

        while not username_passed:
            username = input("Enter your username: ")
            if len(username) <= globals.max_username_length:
                if not functions.user_exist(username):
                    username_passed = True
                else:
                    print("This username is already used.")

        while not password_passed:
            password = input("Enter your password: ")
            password_confirmation = input("Confirm your password: ")

            if password == password_confirmation:
                if password != username:
                    if len(password) >= globals.min_password_length and len(password) <= globals.max_password_length:
                        password_passed = True
                    else:
                        print(f"The password need to be at least {globals.min_password_length} and maximal {globals.max_password_length}")
                else:
                    print("The password cant be same as username")
            else:
                print("Password missmatch.")

        functions.register(username, password)

    def play_blackjack():
        print("[1] Join game")
        print("[2] Check balance")
        
        choice = input()
        if choice.isdecimal():
            if choice == "1":
                # Join server game
                pass
            elif choice == "2":
                print(f"Your balance: {functions.get_user_data(globals.user.username)["balance"]}")
            else:
                pages.play_blackjack()
        else:
            pages.play_blackjack()

    def __init__():
        global mydb, mycursor

        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="casino"
            )

            if mydb.is_connected():
                mycursor = mydb.cursor()

        except:
            print("Couldnt connect to MySQL database")
            return False

        finally:
            if mydb and mydb.is_connected():
                mydb.close()


        #os.system('cls')
        
        print("[1] Login")
        print("[2] Register")
        
        choice = input()
        if choice.isdecimal():
            if choice == "1":
                pages.login()
            elif choice == "2":
                pages.register()
            else:
                pages.__init__()
        else:
            pages.__init__()

if __name__ == "__main__":
    pages.__init__()

# def client_program():
#     host = socket.gethostname()
#     port = 5000

#     client_socket = socket.socket()
#     client_socket.connect((host, port))

#     message = input(" -> ")
#     while message.lower().strip() != 'exit':
#         client_socket.send(message.encode())
#         # data = client_socket.recv(1024).decode()

#         # print('Received from server: ' + data)

#         message = input(" -> ")

#     client_socket.close()

# client_program()