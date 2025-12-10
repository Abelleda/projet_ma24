# Author: Adel Medaric
# Name: client.py
# Date: 03.12.2025

import socket
import json
import threading
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Client")
root.geometry("300x300")
root.resizable(width=False, height=False)

g_username = ""
conn = None

SERVER_IP = "127.0.0.1"
PORT = 5000

# Functions
### Server communication ###
def connect_to_server():
    global conn
    conn = socket.socket()
    conn.connect((SERVER_IP, PORT))

def send(data):
    global conn
    conn.send(json.dumps(data).encode())
    return json.loads(conn.recv(2048).decode())
######



def switch_page(page):
    if page == "login":
        RegisterPage.frm_register.pack_forget()
        LoginPage.frm_login.pack()
    if page == "register":
        LoginPage.frm_login.pack_forget()
        RegisterPage.frm_register.pack()
    if page == "play":
        LoginPage.frm_login.pack_forget()
        RegisterPage.frm_register.pack_forget()
        PlayPage.frm_bet.pack()
        PlayPage.frm_play.pack()

def login():
    print("[Login]")

    global g_username
    user = LoginPage.ent_username.get()
    pwd = LoginPage.ent_password.get()

    connect_to_server()

    response = send({
        "action": "login",
        "username": user,
        "password": pwd
    })

    if response["status"] == "success":
        g_username = response["user"]
        switch_page("play")
        messagebox.showinfo(title="Success", message="Successfully logged in!")
    else:
        messagebox.showinfo(title="Success", message="The username or password is incorrect")

def register():
    print("[Register]")

    user = RegisterPage.ent_username.get()
    pwd = RegisterPage.ent_password.get()
    pwd_confirm = RegisterPage.ent_password_confirm.get()

    if not (pwd == pwd_confirm):
        messagebox.showerror(title="Error", message="Password does not match")
        return

    temp = socket.socket()
    temp.connect((SERVER_IP, PORT))

    temp.send(json.dumps({
        "action": "register",
        "username": user,
        "password": pwd
    }).encode())

    response = json.loads(temp.recv(2048).decode())
    temp.close()

    if response["status"] == "success":
        switch_page("login")
        messagebox.showinfo(title="Success", message="Successfully registered!")
    elif response["status"] == "exists":
        messagebox.showinfo(title="Success", message="Username already exists")
    else:
        messagebox.showinfo(title="Success", message="Failed to register")

def start_game_listener():
    print("Starting game listener")
    while True:
        try:
            data = conn.recv(2048).decode()
            if not data:
                break

            game_response = json.loads(data)
            if game_response.get("action") == "game_start":
                print(game_response)

            if game_response.get("action") == "ui_update":
                print(game_response)

        except:
            break

def play():
    global conn

    bet = PlayPage.ent_bet.get()
    if not bet.isdecimal():
        messagebox.showerror(title="Error", message="Invalid bet")
        return
    
    bet = int(bet)
    data = send({
        "action": "get_data"
    })

    if not (bet <= int(data["data"]["balance"])):
        messagebox.showerror(title="Error", message="You dont have enough balance")
        return

    response = send({
        "action": "join_game"
    })

    if response["status"] == "success":
        print(response)
        t1 = threading.Thread(target=start_game_listener)

###

class LoginPage:
    # Frames
    frm_login = tk.Frame(root)
    frm_username = tk.Frame(frm_login)
    frm_password = tk.Frame(frm_login)
    frm_buttons = tk.Frame(frm_login)
    ###

    # Labels
    lbl_username = tk.Label(frm_username, text="Username")
    lbl_password = tk.Label(frm_password, text="Password")
    ###

    # Entries
    ent_username = tk.Entry(frm_username)
    ent_password = tk.Entry(frm_password, show="*")
    ###

    # Buttons
    btn_login = tk.Button(frm_buttons, text="Login", command=login)
    btn_toregister = tk.Button(frm_buttons, text="register", borderwidth=0, fg="blue", command=lambda: switch_page("register"))
    ###

LoginPage.frm_login.pack()
LoginPage.frm_username.pack()
LoginPage.frm_password.pack()
LoginPage.frm_buttons.pack()
LoginPage.lbl_username.pack(side="left")
LoginPage.lbl_password.pack(side="left")
LoginPage.ent_username.pack(side="right")
LoginPage.ent_password.pack(side="right")
LoginPage.btn_login.pack(side="left")
LoginPage.btn_toregister.pack(side="right")

class RegisterPage:
    # Frames
    frm_register = tk.Frame(root)
    frm_username = tk.Frame(frm_register)
    frm_password = tk.Frame(frm_register)
    frm_password_confirm = tk.Frame(frm_register)
    frm_buttons = tk.Frame(frm_register)
    ###
    
    # Labels
    lbl_username = tk.Label(frm_username, text="Username")
    lbl_password = tk.Label(frm_password, text="Password")
    lbl_password_confirm = tk.Label(frm_password_confirm, text="Confirm Password")
    ###

    # Entries
    ent_username = tk.Entry(frm_username)
    ent_password = tk.Entry(frm_password, show="*")
    ent_password_confirm = tk.Entry(frm_password_confirm, show="*")
    ###

    # Buttons
    btn_register = tk.Button(frm_buttons, text="Register", command=register)
    btn_tologin = tk.Button(frm_buttons, text="login", borderwidth=0, fg="blue",  command=lambda: switch_page("login"))
    ###

RegisterPage.frm_register.pack_forget()
RegisterPage.frm_username.pack()
RegisterPage.frm_password.pack()
RegisterPage.frm_password_confirm.pack()
RegisterPage.frm_buttons.pack()
RegisterPage.lbl_username.pack(side="left")
RegisterPage.lbl_password.pack(side="left")
RegisterPage.lbl_password_confirm.pack(side="left")
RegisterPage.ent_username.pack(side="right")
RegisterPage.ent_password.pack(side="right")
RegisterPage.ent_password_confirm.pack(side="right")
RegisterPage.btn_register.pack(side="left")
RegisterPage.btn_tologin.pack(side="right")

class PlayPage:
    # Frames
    frm_bet = tk.LabelFrame(root)
    frm_play = tk.LabelFrame(root)
    ###

    # Labels
    lbl_bet = tk.Label(frm_bet, text="Enter your bet: ")
    lbl_play = tk.Label(frm_bet, text="Play")
    ###

    # Entries
    ent_bet = tk.Entry(frm_bet)
    ###

    # Buttons
    btn_play = tk.Button(frm_play, text="Play blackjack", command=play)
    ###
PlayPage.frm_bet.pack_forget()
PlayPage.frm_play.pack_forget()
PlayPage.lbl_bet.pack()
PlayPage.lbl_play.pack()
PlayPage.ent_bet.pack()
PlayPage.btn_play.pack()


if __name__ == "__main__":
    root.mainloop()