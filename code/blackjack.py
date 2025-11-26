import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import hashlib
import os

# ---------------- CONFIG ----------------
USERS_FILE = "users.json"
MAX_PLAYERS = 5
CARD_NAMES = ["2","3","4","5","6","7","8","9","10","J","Q","K","AS"]
CARD_IMG_SIZE = (110, 160)
WINDOW_W, WINDOW_H = 1600, 900
MAX_PLAYER_CARDS = 5

# ---------------- UTIL ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

users = load_users()

# ---------------- GUI ROOT ----------------
root = tk.Tk()
root.title("Blackjack - Table Ovale (Multijoueur Simultané)")
root.geometry(f"{WINDOW_W}x{WINDOW_H}")
root.config(bg="#004d00")

# ---------------- Load / placeholder card images ----------------
card_images = {}
def make_placeholder_image(name, size=CARD_IMG_SIZE):
    img = Image.new("RGBA", size, "#ffffff")
    draw = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        f = ImageFont.load_default()
    w,h = draw.textsize(name, font=f)
    draw.rectangle([0,0,size[0]-1,size[1]-1], outline="#000000", width=2)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), name, font=f, fill="#000000")
    return img

def load_card_images():
    for name in CARD_NAMES:
        path = f"gui/cards/{name}.png"
        try:
            img = Image.open(path).convert("RGBA")
        except Exception:
            img = make_placeholder_image(name)
        img = img.resize(CARD_IMG_SIZE, Image.LANCZOS)
        card_images[name] = ImageTk.PhotoImage(img)

load_card_images()

# ---------------- Draw oval table background ----------------
def draw_oval_table(width=1200, height=600):
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0,0,width,height), fill="#006600", outline="#003300", width=8)
    return ImageTk.PhotoImage(img)

table_img = draw_oval_table(1200, 600)
table_label = tk.Label(root, image=table_img, bg="#004d00")
table_label.place(relx=0.5, rely=0.53, anchor="center")

# ---------------- Player positions (oval layout) ----------------
PLAYER_POSITIONS = [
    (0.50, 0.80),   # bottom center (player 1)
    (0.28, 0.74),   # left-bottom (player 2)
    (0.72, 0.74),   # right-bottom (player 3)
    (0.18, 0.58),   # left-top (player 4)
    (0.82, 0.58),   # right-top (player 5)
]
DEALER_POS = (0.50, 0.24)

# ---------------- UI ELEMENTS: Dealer ----------------
dealer_frame = tk.Frame(root, bg="#262626", bd=4, relief="raised")
dealer_frame.place(relx=DEALER_POS[0], rely=DEALER_POS[1], anchor="center", width=420, height=240)
dealer_label = tk.Label(dealer_frame, text="CROUPIER", bg="#262626", fg="white", font=("Arial", 16, "bold"))
dealer_label.place(x=10, y=6)
dealer_total_lbl = tk.Label(dealer_frame, text="Total : ?", bg="#262626", fg="white", font=("Arial", 14))
dealer_total_lbl.place(x=10, y=42)
dealer_canvas = tk.Canvas(dealer_frame, width=400, height=160, bg="#262626", highlightthickness=0)
dealer_canvas.place(x=10, y=68)

# ---------------- UI: Player frames ----------------
player_frames = []
player_canvases = []
player_total_labels = []
player_name_labels = []
player_result_labels = []
player_hit_buttons = []
player_stand_buttons = []

for i in range(MAX_PLAYERS):
    fx, fy = PLAYER_POSITIONS[i]
    frame = tk.Frame(root, bg="#005500", bd=3, relief="ridge")
    frame.place(relx=fx, rely=fy, anchor="center", width=300, height=220)

    name_lbl = tk.Label(frame, text=f"Slot {i+1}", bg="#005500", fg="white", font=("Arial", 12, "bold"))
    name_lbl.place(x=10, y=6)
    total_lbl = tk.Label(frame, text="Total : ?", bg="#005500", fg="white", font=("Arial", 11))
    total_lbl.place(x=10, y=34)

    canvas = tk.Canvas(frame, width=280, height=110, bg="#005500", highlightthickness=0)
    canvas.place(x=10, y=58)

    res_lbl = tk.Label(frame, text="", bg="#005500", fg="yellow", font=("Arial", 10, "bold"))
    res_lbl.place(x=10, y=176)

    hit_btn = tk.Button(frame, text="Hit", width=7, state="disabled")
    hit_btn.place(x=170, y=170)
    stand_btn = tk.Button(frame, text="Stand", width=7, state="disabled")
    stand_btn.place(x=230, y=170)

    player_frames.append(frame)
    player_canvases.append(canvas)
    player_total_labels.append(total_lbl)
    player_name_labels.append(name_lbl)
    player_result_labels.append(res_lbl)
    player_hit_buttons.append(hit_btn)
    player_stand_buttons.append(stand_btn)

# ---------------- State ----------------
active_players = []      # list of usernames in slots order
player_states = {}       # username -> {'hand':[], 'stood':bool, 'busted':bool, 'stats':{...}}
deck = []
dealer_hand = []
game_in_progress = False

# ---------------- Card & hand helpers ----------------
def new_deck():
    d = CARD_NAMES * 4
    random.shuffle(d)
    return d

def card_value(c):
    if c in ("J","Q","K"):
        return 10
    if c == "AS":
        return 11
    return int(c)

def hand_value(hand):
    total = 0
    aces = 0
    for c in hand:
        if c == "AS":
            total += 11
            aces += 1
        else:
            total += card_value(c)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

# ---------------- Display helpers ----------------
def clear_canvas_items(canvas):
    canvas.delete("all")

def draw_hand_on_canvas(canvas, hand):
    clear_canvas_items(canvas)
    if not hand:
        return
    x = 0
    overlap = 30
    for i, c in enumerate(hand):
        img = card_images.get(c)
        # create image reference on canvas (keep ref via attribute)
        canvas.image = getattr(canvas, "image_refs", [])  # list
        if not isinstance(canvas.image, list):
            canvas.image = []
        img_obj = canvas.create_image(10 + x, 10, anchor="nw", image=img)
        # save reference:
        canvas.image.append(img)
        x += CARD_IMG_SIZE[0] - overlap

def update_player_display_by_index(idx):
    if idx >= len(active_players):
        # empty slot -> reset visuals
        player_name_labels[idx].config(text=f"Slot {idx+1}")
        player_total_labels[idx].config(text="Total : ?")
        player_result_labels[idx].config(text="")
        clear_canvas_items(player_canvases[idx])
        player_hit_buttons[idx].config(state="disabled")
        player_stand_buttons[idx].config(state="disabled")
        return
    username = active_players[idx]
    state = player_states[username]
    player_name_labels[idx].config(text=username)
    draw_hand_on_canvas(player_canvases[idx], state['hand'])
    player_total_labels[idx].config(text=f"Total : {hand_value(state['hand'])}")
    if state['busted']:
        player_result_labels[idx].config(text="Bust")
    elif state['stood']:
        player_result_labels[idx].config(text="Stand")
    else:
        player_result_labels[idx].config(text="")

def update_dealer_display(hide_second=True):
    clear_canvas_items(dealer_canvas)
    dx = 10
    overlap = 40
    for i, c in enumerate(dealer_hand):
        if i == 1 and hide_second:
            back_img = make_back_image()
            img = ImageTk.PhotoImage(back_img)
            # store reference on canvas
            dealer_canvas.image_refs = getattr(dealer_canvas, "image_refs", [])
            dealer_canvas.image_refs.append(img)
            dealer_canvas.create_image(dx, 10, anchor="nw", image=img)
        else:
            img = card_images.get(c)
            dealer_canvas.image_refs = getattr(dealer_canvas, "image_refs", [])
            dealer_canvas.image_refs.append(img)
            dealer_canvas.create_image(dx, 10, anchor="nw", image=img)
        dx += CARD_IMG_SIZE[0] - overlap
    if hide_second:
        dealer_total_lbl.config(text="Total : ?")
    else:
        dealer_total_lbl.config(text=f"Total : {hand_value(dealer_hand)}")

def make_back_image(size=CARD_IMG_SIZE):
    # simple red back
    img = Image.new("RGBA", size, "#cc0000")
    draw = ImageDraw.Draw(img)
    draw.rectangle([5,5,size[0]-6,size[1]-6], outline="#330000", width=3)
    try:
        f = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        f = ImageFont.load_default()
    text = "BJ"
    w,h = draw.textsize(text, font=f)
    draw.text(((size[0]-w)/2, (size[1]-h)/2), text, fill="#ffffff", font=f)
    return img

# ---------------- Game flow: deal, hit, stand, dealer play ----------------
def deal_initial():
    global deck, dealer_hand
    deck = new_deck()
    dealer_hand = []
    # reset players hands
    for u in active_players:
        st = player_states[u]
        st['hand'] = []
        st['stood'] = False
        st['busted'] = False
        st['result'] = ""
    # give two cards to each player, dealer gets two
    for _ in range(2):
        for u in active_players:
            player_states[u]['hand'].append(deck.pop())
        dealer_hand.append(deck.pop())
    # update displays
    for idx in range(MAX_PLAYERS):
        update_player_display_by_index(idx)
    update_dealer_display(hide_second=True)
    enable_player_controls()

def enable_player_controls():
    for idx in range(MAX_PLAYERS):
        if idx >= len(active_players):
            player_hit_buttons[idx].config(state="disabled")
            player_stand_buttons[idx].config(state="disabled")
            continue
        username = active_players[idx]
        st = player_states[username]
        if not st['stood'] and not st['busted']:
            player_hit_buttons[idx].config(state="normal")
            player_stand_buttons[idx].config(state="normal")
        else:
            player_hit_buttons[idx].config(state="disabled")
            player_stand_buttons[idx].config(state="disabled")

def disable_all_controls():
    for b in player_hit_buttons + player_stand_buttons:
        b.config(state="disabled")

def player_hit(idx):
    if idx >= len(active_players) or not game_in_progress:
        return
    username = active_players[idx]
    st = player_states[username]
    if st['stood'] or st['busted']:
        return
    # draw
    if not deck:
        deck.extend(new_deck())
    st['hand'].append(deck.pop())
    update_player_display_by_index(idx)
    if hand_value(st['hand']) > 21:
        st['busted'] = True
        player_result_labels[idx].config(text="Bust")
        player_hit_buttons[idx].config(state="disabled")
        player_stand_buttons[idx].config(state="disabled")
    enable_player_controls()
    check_all_done_and_maybe_finish()

def player_stand(idx):
    if idx >= len(active_players) or not game_in_progress:
        return
    username = active_players[idx]
    st = player_states[username]
    st['stood'] = True
    player_result_labels[idx].config(text="Stand")
    player_hit_buttons[idx].config(state="disabled")
    player_stand_buttons[idx].config(state="disabled")
    enable_player_controls()
    check_all_done_and_maybe_finish()

def check_all_done_and_maybe_finish():
    # if at least one active player still playing -> return
    if not active_players:
        return
    for u in active_players:
        s = player_states[u]
        if not (s['stood'] or s['busted']):
            return
    # all finished -> dealer plays
    root.after(300, dealer_play)

def dealer_play():
    global deck, dealer_hand, game_in_progress
    disable_all_controls()
    update_dealer_display(hide_second=False)
    # dealer draws until 17+
    while hand_value(dealer_hand) < 17:
        if not deck:
            deck.extend(new_deck())
        dealer_hand.append(deck.pop())
        update_dealer_display(hide_second=False)
        root.update()
    dv = hand_value(dealer_hand)
    # compare results and update stats
    for idx, u in enumerate(active_players):
        s = player_states[u]
        pv = hand_value(s['hand'])
        if s['busted']:
            res = "Perdu (Bust)"
            s['stats']['losses'] += 1
        else:
            if dv > 21:
                res = "Gagné (Croupier Bust)"
                s['stats']['wins'] += 1
            elif pv > dv:
                res = "Gagné"
                s['stats']['wins'] += 1
            elif pv < dv:
                res = "Perdu"
                s['stats']['losses'] += 1
            else:
                res = "Égalité"
                s['stats']['ties'] += 1
        s['result'] = f"{res} ({pv} vs {dv})"
        player_result_labels[idx].config(text=s['result'])
    game_in_progress = False
    new_round_btn.config(state="normal")

# ---------------- UI: slots menu (left panel) ----------------
menu_frame = tk.Frame(root, bg="#8a8a8a", width=340, height=WINDOW_H)
menu_frame.place(x=0,y=0)
tk.Label(menu_frame, text="Menu Slots & Users", bg="#8a8a8a", fg="white", font=("Arial", 12, "bold")).place(x=10,y=10)

slots_listbox = tk.Listbox(menu_frame, width=28, height=8)
slots_listbox.place(x=12, y=40)

def refresh_slots_listbox():
    slots_listbox.delete(0, tk.END)
    for u in active_players:
        slots_listbox.insert(tk.END, u)

# signup/login windows
def open_signup():
    w = tk.Toplevel(root); w.title("Inscription"); w.geometry("320x260"); w.config(bg="#8a8a8a")
    tk.Label(w, text="Nom utilisateur :", bg="#8a8a8a").pack(pady=6)
    e_user = tk.Entry(w); e_user.pack()
    tk.Label(w, text="Mot de passe :", bg="#8a8a8a").pack(pady=6)
    e_pwd = tk.Entry(w, show="*"); e_pwd.pack()
    tk.Label(w, text="Confirmer :", bg="#8a8a8a").pack(pady=6)
    e_pwd2 = tk.Entry(w, show="*"); e_pwd2.pack()
    msg = tk.Label(w, text="", bg="#8a8a8a", fg="red"); msg.pack(pady=6)
    def do_signup():
        u = e_user.get().strip(); p = e_pwd.get(); p2 = e_pwd2.get()
        if not u or not p or not p2:
            msg.config(text="Tous les champs requis"); return
        if " " in u:
            msg.config(text="Nom sans espace"); return
        if u in users:
            msg.config(text="Utilisateur existe"); return
        if p != p2:
            msg.config(text="Mots de passe diff"); return
        users[u] = hash_password(p)
        save_users(users)
        msg.config(text="Compte créé", fg="green")
    tk.Button(w, text="Créer", command=do_signup, bg="#004225", fg="white").pack(pady=6)

def open_login():
    w = tk.Toplevel(root); w.title("Connexion"); w.geometry("300x180"); w.config(bg="#8a8a8a")
    tk.Label(w, text="Nom utilisateur :", bg="#8a8a8a").pack(pady=6)
    e_user = tk.Entry(w); e_user.pack()
    tk.Label(w, text="Mot de passe :", bg="#8a8a8a").pack(pady=6)
    e_pwd = tk.Entry(w, show="*"); e_pwd.pack()
    msg = tk.Label(w, text="", bg="#8a8a8a", fg="red"); msg.pack(pady=6)
    def do_login():
        u = e_user.get().strip(); p = e_pwd.get()
        if not u or not p:
            msg.config(text="Tous champs requis"); return
        if u not in users:
            msg.config(text="Utilisateur inconnu"); return
        if users[u] != hash_password(p):
            msg.config(text="Mot de passe incorrect"); return
        msg.config(text=f"Connecté : {u}", fg="green")
    tk.Button(w, text="Se connecter", command=do_login, bg="#004225", fg="white").pack(pady=6)

tk.Button(menu_frame, text="S'inscrire", command=open_signup, bg="#FF9900", width=12).place(x=12, y=200)
tk.Button(menu_frame, text="Se connecter", command=open_login, bg="#004225", fg="white", width=12).place(x=170, y=200)

# add existing user to a slot
tk.Label(menu_frame, text="Ajouter joueur existant :", bg="#8a8a8a").place(x=12,y=246)
add_entry = tk.Entry(menu_frame, width=24); add_entry.place(x=12,y=270)
def add_slot():
    name = add_entry.get().strip()
    if not name:
        messagebox.showinfo("Info", "Nom vide"); return
    if name not in users:
        messagebox.showinfo("Info", "Utilisateur inconnu"); return
    if name in active_players:
        messagebox.showinfo("Info", "Déjà ajouté"); return
    if len(active_players) >= MAX_PLAYERS:
        messagebox.showinfo("Info", "Max slots atteints"); return
    active_players.append(name)
    player_states[name] = {'hand':[], 'stood':False, 'busted':False, 'result':"", 'stats':{'wins':0,'losses':0,'ties':0}}
    idx = active_players.index(name)
    player_name_labels[idx].config(text=name)
    refresh_slots_listbox()
    add_entry.delete(0, tk.END)
tk.Button(menu_frame, text="Ajouter", command=add_slot, bg="#3366FF", fg="white").place(x=12,y=300)

def remove_slot():
    sel = slots_listbox.curselection()
    if not sel:
        return
    idx = sel[0]
    name = active_players.pop(idx)
    player_states.pop(name, None)
    # reset UI for that position
    player_name_labels[idx].config(text=f"Slot {idx+1}")
    player_total_labels[idx].config(text="Total : ?")
    player_result_labels[idx].config(text="")
    clear_canvas_items(player_canvases[idx])
    refresh_slots_listbox()
tk.Button(menu_frame, text="Supprimer slot", command=remove_slot, bg="#AA3333", fg="white", width=20).place(x=12,y=335)

# start table / new round
def start_table():
    global game_in_progress
    if not active_players:
        messagebox.showinfo("Info", "Ajoute au moins un joueur")
        return
    if game_in_progress:
        messagebox.showinfo("Info", "Une partie est en cours")
        return
    game_in_progress = True
    for u in active_players:
        st = player_states[u]
        st['hand'] = []
        st['stood'] = False
        st['busted'] = False
        st['result'] = ""
    deal_initial()
    new_round_btn.config(state="disabled")

start_btn = tk.Button(menu_frame, text="Démarrer table", command=start_table, bg="#00A86B", fg="white", width=20)
start_btn.place(x=12, y=375)

def new_round():
    global game_in_progress
    if not active_players:
        messagebox.showinfo("Info", "Aucun joueur")
        return
    if game_in_progress:
        messagebox.showinfo("Info", "Partie en cours")
        return
    game_in_progress = True
    for u in active_players:
        st = player_states[u]
        st['hand'] = []
        st['stood'] = False
        st['busted'] = False
        st['result'] = ""
    deal_initial()
    new_round_btn.config(state="disabled")

new_round_btn = tk.Button(menu_frame, text="Nouvelle manche", command=new_round, bg="#FFA500", width=20, state="disabled")
new_round_btn.place(x=12, y=410)

# stats viewer
def show_stats():
    if not active_players:
        messagebox.showinfo("Info", "Aucun joueur")
        return
    w = tk.Toplevel(root); w.title("Stats"); w.geometry("360x260"); w.config(bg="#8a8a8a")
    y = 10
    for u in active_players:
        s = player_states[u]['stats']
        lbl = tk.Label(w, text=f"{u}: Vic {s['wins']} - Def {s['losses']} - Eq {s['ties']}", bg="#8a8a8a", fg="white")
        lbl.place(x=10, y=y)
        y += 30

tk.Button(menu_frame, text="Afficher stats", command=show_stats, bg="#3366FF", fg="white", width=20).place(x=12, y=450)

# instructions
instr = (
    "Procédure:\n"
    "1) Créer / connecter comptes\n"
    "2) Ajouter jusqu'à 5 joueurs\n"
    "3) Démarrer table\n"
    "4) Chaque joueur clique Hit / Stand\n"
    "5) Quand tous terminent, croupier joue"
)
tk.Label(menu_frame, text=instr, bg="#8a8a8a", fg="white", justify="left", wraplength=300).place(x=12, y=495)

# ---------------- Attach player buttons callbacks ----------------
def make_hit(idx):
    return lambda: player_hit(idx)

def make_stand(idx):
    return lambda: player_stand(idx)

for i in range(MAX_PLAYERS):
    player_hit_buttons[i].config(command=make_hit(i))
    player_stand_buttons[i].config(command=make_stand(i))

# ---------------- Initialize empty UI slots ----------------
for i in range(MAX_PLAYERS):
    update_player_display_by_index(i)

# ---------------- Start main loop ----------------
root.mainloop()
