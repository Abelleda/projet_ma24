import os
import sys
import mysql.connector 
import socket
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.sv_main import functions

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
        
class pages:
    def login():
        os.system('cls')

        print("[Login Page]")
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if functions.login(username, password):
            print(f"Welcome {globals.user.username}!")
            pages.play_blackjack()
        else:
            pages.login()

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

        if functions.register(username, password):
            pages.__init__()

    def play_blackjack():
        os.system('cls')

        print("[Game Page]")
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

        os.system('cls')
        
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