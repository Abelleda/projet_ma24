# import tkinter as tk
# from PIL import Image, ImageTk


# window = tk.Tk()
# window.title("Black Jack")
# window.geometry("1980x1080")
# image = tk.PhotoImage(file="image.png")
# label = tk.Label(window, image=image)
# label.pack()    



# window.mainloop()


import random
import tkinter as tk
from PIL import Image, ImageTk

# ----------------------
#  INITIALISATION
# ----------------------
window = tk.Tk()
window.title("Black Jack")
window.geometry("1980x1080")

# TABLE
table_img = Image.open("image.png")
table_img = table_img.resize((1980, 1080), Image.LANCZOS)
table_photo = ImageTk.PhotoImage(table_img)

table_label = tk.Label(window, image=table_photo)
table_label.place(x=0, y=0)


# ----------------------
#  CHARGEMENT DES CARTES
# ----------------------

# NOMS EXACTEMENT COMME TES FICHIERS
card_names = ["2","3","4","5","6","7","8","9","10","J","Q","K","AS"]

card_images = {}

def load_card_images():
    for name in card_names:
        img = Image.open(f"cards/{name}.png")
        img = img.resize((140, 200), Image.LANCZOS)  # taille carte
        card_images[name] = ImageTk.PhotoImage(img)

load_card_images()


# ----------------------
#  LOGIQUE DU JEU
# ----------------------

def new_deck():
    # Ici pas de couleurs ♣♥♦♠ donc on fait un deck simple
    deck = card_names.copy() * 4  # 4 exemplaires de chaque comme vrai blackjack
    random.shuffle(deck)
    return deck

def card_value(card):
    if card in ["J","Q","K"]:
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

    # Ajustement As = 1 si dépasse 21
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total


# ----------------------
#  AFFICHAGE DES CARTES
# ----------------------

dealer_frame = tk.Frame(window, bg="green")
dealer_frame.place(x=700, y=150)

player_frame = tk.Frame(window, bg="green")
player_frame.place(x=700, y=500)

dealer_labels = []
player_labels = []

def show_hand(frame, hand, labels_list):
    for lbl in labels_list:
        lbl.destroy()
    labels_list.clear()

    x = 0
    for card in hand:
        lbl = tk.Label(frame, image=card_images[card], bg="green")
        lbl.place(x=x, y=0)
        labels_list.append(lbl)
        x += 150


# ----------------------
#  ACTIONS JEU
# ----------------------

def start_game():
    global deck, player_hand, dealer_hand

    deck = new_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    show_hand(player_frame, player_hand, player_labels)
    show_hand(dealer_frame, [dealer_hand[0]], dealer_labels)

    result_label.config(text="")

def hit():
    player_hand.append(deck.pop())
    show_hand(player_frame, player_hand, player_labels)

    if hand_value(player_hand) > 21:
        result_label.config(text=" Vous avez dépassé 21 !")

def stand():
    # Le croupier tire
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deck.pop())

    show_hand(dealer_frame, dealer_hand, dealer_labels)

    pv = hand_value(player_hand)
    dv = hand_value(dealer_hand)

    if dv > 21:
        result_label.config(text=" Le croupier dépasse 21, vous gagnez !")
    elif pv > dv:
        result_label.config(text=" Vous gagnez !")
    elif pv < dv:
        result_label.config(text=" Vous perdez !")
    else:
        result_label.config(text=" Égalité !")


# ----------------------
#  BOUTONS
# ----------------------
btn_frame = tk.Frame(window, bg="darkgreen")
btn_frame.place(x=820, y=400)

tk.Button(btn_frame, text="Nouvelle Partie", command=start_game, width=15).pack(pady=10)
tk.Button(btn_frame, text="Hit", command=hit, width=15).pack(pady=10)
tk.Button(btn_frame, text="Stand", command=stand, width=15).pack(pady=10)

result_label = tk.Label(window, text="", font=("Arial", 22), bg="darkgreen", fg="white")
result_label.place(x=780, y=350)

start_game()

