import socket
import threading
import json
import mysql.connector
import bcrypt

mydb = None
mycursor = None
clients = {}

# ---------------------- DB CONNECTION ----------------------
def connect_db():
    global mydb, mycursor
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="casino"
        )
        mycursor = mydb.cursor()
        print("[SERVER] Connected to MySQL")

    except Exception as e:
        print("[SERVER] Could not connect to MySQL:", e)

# ---------------------- FUNCTIONS ----------------------
def user_exist(username):
    mycursor.execute("SELECT id FROM users WHERE username=%s", (username,))
    return mycursor.fetchone() is not None

def get_user(username):
    mycursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    row = mycursor.fetchone()
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
    try:
        mycursor.execute("INSERT INTO users(username, password) VALUES (%s,%s)", (username, password))
        mydb.commit()
        return True
    except:
        return False

def login_user(username, password):
    userdata = get_user(username)
    if userdata and verify_password(password, userdata["password"]):
        print("Good password")
        return userdata
    
    return None

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(password, stored_password):
    return bcrypt.checkpw(password.encode(), stored_password.encode())

# ---------------------- CLIENT THREAD ----------------------
def handle_client(conn, addr):
    print(f"[SERVER] Client connected: {addr}")
    username = None

    while True:
        try:
            data = conn.recv(2048).decode()
            if not data:
                break

            request = json.loads(data)

            # ------- LOGIN -------
            if request["action"] == "login":
                result = login_user(request["username"], request["password"])
                if result:
                    username = result["username"]
                    if username in clients:
                        conn.send(json.dumps({"status": "failed", "description": "This account is already connected to the server."}).encode())
                    else:
                        clients[username] = conn
                        conn.send(json.dumps({"status": "success", "user": username}).encode())
                else:
                    conn.send(json.dumps({"status": "failed"}).encode())

            # ------- REGISTER -------
            elif request["action"] == "register":
                if user_exist(request["username"]):
                    conn.send(json.dumps({"status": "exists"}).encode())
                else:
                    if register_user(request["username"], hash_password(request["password"])):
                        conn.send(json.dumps({"status": "success"}).encode())
                    else:
                        conn.send(json.dumps({"status": "failed"}).encode())

            # ------- DISCONNECT -------
            elif request["action"] == "disconnect":
                print(f"[SERVER] {username} disconnected")
                if username in clients:
                    del clients[username]
                conn.send(json.dumps({"status": "success"}).encode())
                break

        except Exception as e:
            print("[SERVER ERROR]:", e)
            break

    if username in clients:
        del clients[username]

    conn.close()
    print(f"[SERVER] Connection closed: {addr}")


# ---------------------- SERVER START ----------------------

def start_server():
    connect_db()

    server = socket.socket()
    server.bind(("0.0.0.0", 5000))
    server.listen()

    print("[SERVER] Running on port 5000")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    start_server()