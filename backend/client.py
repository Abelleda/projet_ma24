import socket
import json

g_username = ""
conn = None

SERVER_IP = "127.0.0.1"
PORT = 5000

# ----------- FUNCTIONS -----------
def connect_to_server():
    global conn
    conn = socket.socket()
    conn.connect((SERVER_IP, PORT))

def send(data):
    global conn
    conn.send(json.dumps(data).encode())
    return json.loads(conn.recv(2048).decode())

# ---------------- CLIENT PAGES ----------------
def game_page():
    global conn
    print("[1] Play Blackjack")

    choice = input()

    if choice == "2":
        response = send({
            "action": "disconnect",
            "username": g_username
        })

        print("Disconnected:", response["status"])
        conn.close()
        conn = None
        exit()

def login_page():
    global g_username

    print("[Login]")
    user = input("Username: ")
    pwd = input("Password: ")

    connect_to_server()

    response = send({
        "action": "login",
        "username": user,
        "password": pwd
    })

    if response["status"] == "success":
        g_username = response["user"]
        print("Logged in as:", g_username)
        game_page()
    else:
        print("Login failed.")
        login_page()

def register_page():
    print("[Register]")
    user = input("Username: ")
    pwd = input("Password: ")

    temp = socket.socket()
    temp.connect((SERVER_IP, PORT))

    temp.send(json.dumps({
        "action": "register",
        "username": user,
        "password": pwd
    }).encode())

    response = json.loads(temp.recv(2048).decode())
    temp.close()

    if response["status"] == "exists":
        print("Username already exists!")
    elif response["status"] == "success":
        print("Registered successfully!")   
    else:
        print("Registration failed!")

    main_menu()

def main_menu():
    print("[1] Login")
    print("[2] Register")

    choice = input()

    if choice == "1":
        login_page()
    elif choice == "2":
        register_page()
    else:
        main_menu()

if __name__ == "__main__":
    main_menu()