# Author: Adel Medaric
# Name: server.py
# Date: 03.12.2025

import socket
import threading
import json
import mysql.connector
import bcrypt

mydb = None

clients = {}
game_clients = {}

min_bet = 20
max_bet = 500

# Database
def connect_db():
    global mydb
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="casino",
            autocommit=True
        )
        print("[SERVER] Connected to MySQL")

    except Exception as e:
        print("[SERVER] Could not connect to MySQL:", e)
###

# Functions
def user_exist(username):
    global mydb
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT id FROM users WHERE username=%s", (username,))
    exists = mycursor.fetchone() is not None
    mycursor.close()
    return exists

def get_user(username):
    global mydb
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    row = mycursor.fetchone()
    mycursor.close()
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "password": row[2],
            "balance": row[3],
            "date_created": row[4]
        }
    
    return None

def register_user(username, password):
    global mydb
    try:
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("INSERT INTO users(username, password) VALUES (%s,%s)", (username, password))
        mydb.commit()
        mycursor.close()
        return True
    except:
        return False

def login_user(username, password):
    userdata = get_user(username)
    if userdata and verify_password(password, userdata["password"]):
        return userdata
    
    return None

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(password, stored_password):
    return bcrypt.checkpw(password.encode(), stored_password.encode())

def update_clients_ui():
    for client in game_clients:
        try:
            client.send(json.dumps({
                "action": "ui_update",
                "players": game_clients
            }).encode())
        except:
            pass

def broadcast_game_start():
    for client in game_clients:
        try:
            client.send(json.dumps({
                "action": "game_start",
                "players": list(game_clients.values())
            }).encode())
        except:
            pass

    print(f"[SERVER] Game is starting with {game_clients}")
###

# Client thread
def handle_client(conn, addr):
    print(f"[SERVER] Client connected: {addr}")

    while True:
        try:
            data = conn.recv(2048).decode()
            if not data:
                break

            request = json.loads(data)
            action = request.get("action")

            # LOGIN
            if action == "login":
                result = login_user(request["username"], request["password"])
                if result:
                    username = result["username"]
                    if username in clients.values():
                        conn.send(json.dumps({"status": "failed", "description": "User already connected"}).encode())
                    else:
                        clients[conn] = username
                        conn.send(json.dumps({"status": "success", "user": username}).encode())
                else:
                    conn.send(json.dumps({"status": "failed"}).encode())

            # REGISTER
            elif action == "register":
                if user_exist(request["username"]):
                    conn.send(json.dumps({"status": "exists"}).encode())
                else:
                    if register_user(request["username"], hash_password(request["password"])):
                        conn.send(json.dumps({"status": "success"}).encode())
                    else:
                        conn.send(json.dumps({"status": "failed"}).encode())

            # JOIN GAME
            elif action == "join_game":
                username = clients[conn]
                bet = request.get("bet")

                if len(game_clients) < 2:
                    game_clients[conn] = {
                        "username": username,
                        "bet": bet
                    }
                    print(f"[SERVER] Player '{username}' with: {bet}$ of bet joined the game")
                    conn.send(json.dumps({
                        "status": "success",
                        "description": "Successfully joined the game"
                    }).encode())

                    update_clients_ui(game_clients)
                    
                    if len(game_clients) == 2:
                        broadcast_game_start()
                else:
                    conn.send(json.dumps({
                        "status": "failed",
                        "description": "Game is full"
                    }).encode())

            # DISCONNECT
            elif action == "disconnect":
                print(f"[SERVER] '{clients[conn]}' disconnected")
                conn.send(json.dumps({"status": "success"}).encode())
                break

            # GET DATA
            elif action == "get_data":
                data = get_user(clients[conn])
                if data:
                    conn.send(json.dumps({
                        "status": "success",
                        "data": data
                    }, default=str).encode())
                else:
                    conn.send(json.dumps({
                        "status": "failed"
                    }))

        except Exception as e:
            print("[SERVER ERROR]:", e)
            break

    if conn in game_clients:
        send_notif_to_all_players(f"{game_clients[conn]} left")

        del game_clients[conn]

    if conn in clients:
        del clients[conn]

    conn.close()
    print(f"[SERVER] Connection closed: {addr}")
###

# Server start
def start_server():
    connect_db()

    server = socket.socket()
    server.bind(("0.0.0.0", 5000))
    server.listen()

    print("[SERVER] Running on port 5000")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
###

if __name__ == "__main__":
    start_server()