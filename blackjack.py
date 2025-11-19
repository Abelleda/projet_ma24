import random
import tkinter as tk
from PIL import Image, ImageTk

window = tk.Tk()
window.title("Black Jack")
window.geometry("1920x1080")
window.config(bg="darkgreen")

# --- CARTES DISPONIBLES ---
card_names = ["2","3","4","5","6","7","8","9","10","J","Q","K","AS"]

MAX_PLAYER_CARDS = 6


# --- STOCKAGE GLOBAL DES IMAGES (IMPORTANT !) ---
card_images = {}

def load_card_images():
    for name in card_names:
        img = Image.open(f"cards/{name}.png")
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

# --- FRAMES ---
dealer_frame = tk.Frame(window, bg="green", anchor="center", eight=220)
dealer_frame.place(x=650, y=120)

player_frame = tk.Frame(window, bg="green", width=1000, height=220)
player_frame.place(x=650, y=480)

dealer_labels = []
player_labels = []

# LES SCORES
dealer_value_label = tk.Label(window, text="Total croupier : ?", font=("Arial", 20), bg="darkgreen", fg="white")
dealer_value_label.place(x=400, y=200)

player_value_label = tk.Label(window, text="Total joueur : 0", font=("Arial", 20), bg="darkgreen", fg="white")
player_value_label.place(x=400, y=600)

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
    player_value_label.config(text=f"Total joueur : {hand_value(player_hand)}")

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

# --- BOUTONS ---
btn_frame = tk.Frame(window, bg="darkgreen")

# placé vers la droite de la fenêtre, centré verticalement
btn_frame.place(relx=0.85, rely=0.5, anchor="center")
new_button = tk.Button(btn_frame,
    text="Nouvelle Partie",
    command=start_game,   # <-- la bonne fonction !
    bg="#FF0000",         # vert foncé casino
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
    bg="#004225",           # vert foncé casino
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
    bg="#004225",            # vert foncé casino
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

start_game()

window.mainloop()