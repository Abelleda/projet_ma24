import random
import tkinter as tk
from PIL import Image, ImageTk
import json
import hashlib

# --------- GESTION UTILISATEURS ---------

USERS_FILE = "users.json"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

users = load_users()

# --------- FENÊTRE PRINCIPALE DU JEU ---------

window = tk.Tk()
window.title("Black Jack")
window.geometry("1920x1080")
window.config(bg="darkgreen")

# --- CARTES DISPONIBLES ---
card_names = ["2","3","4","5","6","7","8","9","10","J","Q","K","AS"]

MAX_PLAYER_CARDS = 5

# --- NOM DU JOUEUR ---
player_name = "Joueur"

# --- STOCKAGE GLOBAL DES IMAGES (IMPORTANT !) ---
card_images = {}

def load_card_images():
    for name in card_names:
        img = Image.open(f"gui/cards/{name}.png")
        img = img.resize((140, 200), Image.LANCZOS)
        card_images[name] = ImageTk.PhotoImage(img)   # Référence conservée

load_card_images()

# --- CREATION DU DECK ---
def new_deck(): 
    deck = card_names * 4
    random.shuffle(deck)
    return deck

# --- VALEUR DES CARTES ---
def card_value(card):                           
    if card in ["J", "Q", "K"]:
        return 10
    if card == "AS":
        return 11
    return int(card)

def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        if card == "AS":
            total += 11
            aces += 1
        else:
            total += card_value(card)

    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total

# --- FRAMES DU JEU ---
dealer_frame = tk.Frame(window, bg="green", width=800, height=220)
dealer_frame.place(x=650, y=120)

player_frame = tk.Frame(window, bg="green", width=800, height=220)
player_frame.place(x=650, y=480)

dealer_labels = []
player_labels = []

# LES SCORES
dealer_value_label = tk.Label(window, text="Total croupier : ?", font=("Arial", 20), bg="darkgreen", fg="white")
dealer_value_label.place(x=400, y=200)

player_value_label = tk.Label(window, text=f"Total {player_name} : 0", font=("Arial", 20), bg="darkgreen", fg="white")
player_value_label.place(x=400, y=600)

# Nom du joueur affiché dans la fenêtre de jeu
player_name_label = tk.Label(window, text="Joueur : ?", font=("Arial", 22, "bold"),
                             bg="darkgreen", fg="white")
player_name_label.place(x=50, y=50)

# --- AFFICHAGE DES MAINS ---
def show_hand(frame, hand, labels_list):
    # Effacer les anciennes cartes
    for lbl in labels_list:
        lbl.destroy()
    labels_list.clear()

    x = 0
    for card in hand:
        lbl = tk.Label(frame, image=card_images[card], bg="green")
        lbl.image = card_images[card]   # garder une référence
        lbl.place(x=x, y=0)
        labels_list.append(lbl)
        x += 150

def update_values(show_dealer_total=False):
    # total du joueur
    player_value_label.config(text=f"Total {player_name} : {hand_value(player_hand)}")

    # total du croupier
    if show_dealer_total:
        dealer_value_label.config(text=f"Total croupier : {hand_value(dealer_hand)}")
    else:
        dealer_value_label.config(text="Total croupier : ?")

# --- NOUVELLE PARTIE ---
def start_game():
    global deck, player_hand, dealer_hand

    deck = new_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    show_hand(player_frame, player_hand, player_labels)
    show_hand(dealer_frame, [dealer_hand[0]], dealer_labels)

    # Met à jour les totaux au début de la partie
    update_values(show_dealer_total=False)

    result_label.config(text="")

    hit_button.config(state="normal")
    stand_button.config(state="normal")

# --- HIT ---
def hit():
    # Si le joueur a déjà le nombre max de cartes, on bloque
    if len(player_hand) >= MAX_PLAYER_CARDS:
        result_label.config(text=" Vous avez déjà le nombre maximal de cartes.")
        hit_button.config(state="disabled")
        return

    # Sinon on pioche une carte
    player_hand.append(deck.pop())
    show_hand(player_frame, player_hand, player_labels)
    update_values(show_dealer_total=False)

    # Si le joueur dépasse 21 -> fin de partie
    if hand_value(player_hand) > 21:
        result_label.config(text=" Vous avez dépassé 21 !")
        hit_button.config(state="disabled")
        stand_button.config(state="disabled")

# --- STAND ---
def stand():
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.pop())

    show_hand(dealer_frame, dealer_hand, dealer_labels)
    show_hand(player_frame, player_hand, player_labels)

    update_values(show_dealer_total=True)

    pv = hand_value(player_hand)
    dv = hand_value(dealer_hand)

    if dv > 21:
        result_label.config(text=" Le croupier dépasse 21, vous avez gagné !")
    elif pv > dv:
        result_label.config(text=" Vous avez gagné !")
    elif pv < dv:
        result_label.config(text=" Vous avez perdu !")
    else:
        result_label.config(text=" Égalité !")

# --- BOUTONS DU JEU ---
btn_frame = tk.Frame(window, bg="darkgreen")
btn_frame.place(relx=0.85, rely=0.5, anchor="center")

new_button = tk.Button(btn_frame,
    text="Nouvelle Partie",
    command=start_game,
    bg="#FF0000",
    fg="white",
    activebackground="#ff0000",
    activeforeground="#ffffff",
    font=("Arial", 18, "bold"),
    width=15,
    relief="ridge",
    bd=4
)
new_button.pack(pady=10)

hit_button = tk.Button(btn_frame,
    text="Hit",
    command=hit,
    bg="#004225",
    fg="white",
    activebackground="#006b3c",
    activeforeground="#ffffff",
    font=("Arial", 18, "bold"),
    width=15,
    relief="ridge",
    bd=4
)
hit_button.pack(pady=10)

stand_button = tk.Button(btn_frame,
    text="Stand",
    command=stand,
    bg="#004225",
    fg="white",
    activebackground="#006b3c",
    activeforeground="#ffffff",
    font=("Arial", 18, "bold"),
    width=15,
    relief="ridge",
    bd=4
)
stand_button.pack(pady=10)

# --- RESULTAT ---
result_label = tk.Label(window, text="", font=("Arial", 22), bg="darkgreen", fg="white")
result_label.place(x=780, y=350)

# -------------------------------------------------
#           FENÊTRE DE MENU (LOGIN / SIGNUP)
# -------------------------------------------------

# On cache la fenêtre principale au début
window.withdraw()

menu_window = tk.Toplevel(window)
menu_window.title("Black Jack - Menu")
menu_window.geometry("500x350")
menu_window.config(bg="grey")

title_label = tk.Label(menu_window, text="BLACK JACK", font=("Arial", 40, "bold"), bg="grey", fg="white")
title_label.pack(pady=20)

subtitle_label = tk.Label(menu_window, text="Veuillez vous connecter ou vous inscrire", font=("Arial", 14),
                          bg="grey", fg="white")
subtitle_label.pack(pady=5)

# --- FENÊTRE D'INSCRIPTION ---
def open_signup_window():
    signup_win = tk.Toplevel(menu_window)
    signup_win.title("Inscription")
    signup_win.geometry("400x300")
    signup_win.config(bg="grey")

    tk.Label(signup_win, text="Nom d'utilisateur :", font=("Arial", 14), bg="grey", fg="white").pack(pady=5)
    username_entry = tk.Entry(signup_win, font=("Arial", 14), width=20)
    username_entry.pack(pady=5)

    tk.Label(signup_win, text="Mot de passe :", font=("Arial", 14), bg="grey", fg="white").pack(pady=5)
    password_entry = tk.Entry(signup_win, font=("Arial", 14), width=20, show="*")
    password_entry.pack(pady=5)

    tk.Label(signup_win, text="Confirmer le mot de passe :", font=("Arial", 14), bg="grey", fg="white").pack(pady=5)
    confirm_entry = tk.Entry(signup_win, font=("Arial", 14), width=20, show="*")
    confirm_entry.pack(pady=5)

    message_label = tk.Label(signup_win, text="", font=("Arial", 10), bg="grey", fg="red")
    message_label.pack(pady=5)

    def do_signup():
        global player_name, users

        username = username_entry.get().strip()
        pwd = password_entry.get()
        pwd2 = confirm_entry.get()

        if username == "" or pwd == "" or pwd2 == "":
            message_label.config(text="Tous les champs sont obligatoires.")
            return

        if " " in username:
            message_label.config(text="Le nom ne doit pas contenir d'espace.")
            return

        if username in users:
            message_label.config(text="Ce nom d'utilisateur existe déjà.")
            return

        if pwd != pwd2:
            message_label.config(text="Les mots de passe ne correspondent pas.")
            return

        # Création du compte
        users[username] = hash_password(pwd)
        save_users()

        # Connexion automatique
        player_name = username
        player_value_label.config(text=f"Total {player_name} : 0")
        player_name_label.config(text=f"Joueur : {player_name}")

        signup_win.destroy()
        menu_window.destroy()
        window.deiconify()
        start_game()

    tk.Button(signup_win,
              text="Créer le compte",
              command=do_signup,
              bg="#004225",
              fg="white",
              activebackground="#006b3c",
              activeforeground="#ffffff",
              font=("Arial", 14, "bold"),
              width=18,
              relief="ridge",
              bd=4).pack(pady=15)

# --- FENÊTRE DE CONNEXION ---
def open_login_window():
    login_win = tk.Toplevel(menu_window)
    login_win.title("Connexion")
    login_win.geometry("400x250")
    login_win.config(bg="grey")

    tk.Label(login_win, text="Nom d'utilisateur :", font=("Arial", 14), bg="grey", fg="white").pack(pady=5)
    username_entry = tk.Entry(login_win, font=("Arial", 14), width=20)
    username_entry.pack(pady=5)

    tk.Label(login_win, text="Mot de passe :", font=("Arial", 14), bg="grey", fg="white").pack(pady=5)
    password_entry = tk.Entry(login_win, font=("Arial", 14), width=20, show="*")
    password_entry.pack(pady=5)

    message_label = tk.Label(login_win, text="", font=("Arial", 10), bg="grey", fg="red")
    message_label.pack(pady=5)

    def do_login():
        global player_name

        username = username_entry.get().strip()
        pwd = password_entry.get()

        if username == "" or pwd == "":
            message_label.config(text="Tous les champs sont obligatoires.")
            return

        if username not in users:
            message_label.config(text="Utilisateur inexistant.")
            return

        if users[username] != hash_password(pwd):
            message_label.config(text="Mot de passe incorrect.")
            return

        # Connexion réussie
        player_name = username
        player_value_label.config(text=f"Total {player_name} : 0")
        player_name_label.config(text=f"Joueur : {player_name}")

        login_win.destroy()
        menu_window.destroy()
        window.deiconify()
        start_game()

    tk.Button(login_win,
              text="Se connecter",
              command=do_login,
              bg="#004225",
              fg="white",
              activebackground="#006b3c",
              activeforeground="#ffffff",
              font=("Arial", 14, "bold"),
              width=18,
              relief="ridge",
              bd=4).pack(pady=15)

# --- BOUTONS MENU ---
btn_menu_frame = tk.Frame(menu_window, bg="grey")
btn_menu_frame.pack(pady=30)

login_button = tk.Button(btn_menu_frame,
    text="Se connecter",
    command=open_login_window,
    bg="#004225",
    fg="white",
    activebackground="#006b3c",
    activeforeground="#ffffff",
    font=("Arial", 16, "bold"),
    width=15,
    relief="ridge",
    bd=4
)
login_button.pack(side="left", padx=10)

signup_button = tk.Button(btn_menu_frame,
    text="S'inscrire",
    command=open_signup_window,
    bg="#FF9900",
    fg="white",
    activebackground="#ffb84d",
    activeforeground="#ffffff",
    font=("Arial", 16, "bold"),
    width=15,
    relief="ridge",
    bd=4
)
signup_button.pack(side="left", padx=10)

window.mainloop()
