import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont


# ---------------- CONFIG ----------------
MAX_PLAYERS = 3
CARD_NAMES = ["2","3","4","5","6","7","8","9","10","J","Q","K","AS"]
CARD_IMG_SIZE = (80, 120)
WINDOW_W, WINDOW_H = 1600, 900



import tkinter as tk

def create_start_window():
    start_window = tk.Tk()
    start_window.title("Blackjack")
    start_window.geometry("400x300")
    start_window.config(bg="#222222")

    label = tk.Label(start_window, text="Bienvenue dans le Blackjack",
                     bg="#222222", fg="white", font=("Arial", 16, "bold"))
    label.pack(pady=20)

    def open_main_game():
        start_window.destroy()
        
        launch_blackjack_ui()   # Ton jeu principal

    def senscrire_in_game():
        # Disable the main menu "S'inscrire" button while the Toplevel is open
        senscrire_button.config(state="disabled")
        start_button.config(state="disabled")
        senscrire_window = tk.Toplevel()  # <<< IMPORTANT : Toplevel, pas Tk()
        senscrire_window.title("Inscription")
        senscrire_window.geometry("400x300")
        senscrire_window.config(bg="#222222")

        # Exemple contenu
        tk.Label(senscrire_window, text="Créer un compte",
                 bg="#222222", fg="white", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Label(senscrire_window, text="Nom d'utilisateur :",
                 bg="#222222", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Entry(senscrire_window, width=30).pack(pady=10)

        tk.Label(senscrire_window, text="Mot de passe :",
                 bg="#222222", fg="white", font=("Arial", 12)).pack(pady=5)
        tk.Entry(senscrire_window, width=30, show="*").pack(pady=10)

        # When the registration window is closed, re-enable the main "S'inscrire" button
        def on_close():
            try:
                senscrire_button.config(state="normal")
                start_button.config(state="normal")
            except Exception:
                pass
            senscrire_window.destroy()

        senscrire_window.protocol("WM_DELETE_WINDOW", on_close)

        tk.Button(senscrire_window, text="Fermer",
                  command=on_close,
                  bg="#AA0000", fg="white").pack(pady=10)


    start_button = tk.Button(start_window, text="Commencer",
                             command=open_main_game,
                             bg="#00A86B", fg="white", font=("Arial", 14), width=25)
    start_button.pack(pady=20)

    senscrire_button = tk.Button(start_window, text="S'inscrire",
                             command=senscrire_in_game,
                             bg="#00A86B", fg="white", font=("Arial", 14), width=25)
    senscrire_button.pack(pady=20)

    start_window.mainloop()


# ---------------- Main UI ----------------
def launch_blackjack_ui():
    root = tk.Tk()
    root.title("Blackjack - Table Ovale (Multijoueur Simultané)")
    root.geometry(f"{WINDOW_W}x{WINDOW_H}")
    root.config(bg="#004d00")

    # State
    active_players = []
    player_states = {}
    deck = []
    dealer_hand = []
    game_in_progress = False
    card_images = {}

    # ---------- Images ----------
    def make_placeholder_image(name, size=CARD_IMG_SIZE):
        img = Image.new("RGBA", size, "#ffffff")
        draw = ImageDraw.Draw(img)
        try:
            f = ImageFont.truetype("arial.ttf", 36)
        except:
            f = ImageFont.load_default()
        w,h = draw.textsize(name, font=f)
        draw.rectangle([0,0,size[0]-1,size[1]-1], outline="#000000", width=2)
        draw.text(((size[0]-w)/2, (size[1]-h)/2), name, font=f, fill="#000000")
        return img

    def load_card_images():
        for name in CARD_NAMES:
            try:
                img = Image.open(f"gui/cards/{name}.png").convert("RGBA")
            except:
                img = make_placeholder_image(name)
            img = img.resize(CARD_IMG_SIZE, Image.LANCZOS)
            card_images[name] = ImageTk.PhotoImage(img)

    def make_back_image(size=CARD_IMG_SIZE):
        img = Image.new("RGBA", size, "#cc0000")
        draw = ImageDraw.Draw(img)
        draw.rectangle([5,5,size[0]-6,size[1]-6], outline="#330000", width=3)
        try:
            f = ImageFont.truetype("arial.ttf", 36)
        except:
            f = ImageFont.load_default()
        w,h = draw.textsize("BJ", font=f)
        draw.text(((size[0]-w)/2, (size[1]-h)/2),"BJ",font=f,fill="white")
        return img

    load_card_images()

    # ---------- Table ----------
    def draw_oval_table(width=1200, height=600):
        img = Image.new("RGBA",(width,height),(0,0,0,0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0,0,width,height), fill="#006600", outline="#003300", width=8)
        return ImageTk.PhotoImage(img)

    table_img = draw_oval_table()
    table_label = tk.Label(root, image=table_img, bg="#004d00")
    table_label.place(relx=0.5, rely=0.53, anchor="center")

    # ---------- Positions ----------
    PLAYER_POSITIONS = [
        (0.50, 0.80),
        (0.28, 0.74),
        (0.72, 0.74),
        (0.18, 0.58),
        (0.82, 0.58)
    ]
    DEALER_POS = (0.50, 0.24)

    # ---------- Dealer ----------
    dealer_frame = tk.Frame(root, bg="#262626", bd=4, relief="raised")
    dealer_frame.place(relx=DEALER_POS[0], rely=DEALER_POS[1], anchor="center", width=420, height=250)
    tk.Label(dealer_frame,text="CROUPIER",bg="#262626",fg="white",font=("Arial",16,"bold")).place(x=10,y=6)
    dealer_total_lbl = tk.Label(dealer_frame,text="Total : ?",bg="#262626",fg="white",font=("Arial",14))
    dealer_total_lbl.place(x=10,y=42)
    dealer_canvas = tk.Canvas(dealer_frame,width=400,height=120,bg="#262626",highlightthickness=0)
    dealer_canvas.place(x=10,y=68)

    # ---------- Players ----------
    player_frames=[]
    player_canvases=[]
    player_total_labels=[]
    player_name_labels=[]
    player_result_labels=[]
    player_hit_buttons=[]
    player_stand_buttons=[]

    for i in range(MAX_PLAYERS):
        fx,fy = PLAYER_POSITIONS[i]
        frame = tk.Frame(root,bg="#005500",bd=3,relief="ridge")
        frame.place(relx=fx,rely=fy,anchor="center",width=300,height=250)

        name_lbl = tk.Label(frame,text=f"Slot {i+1}",bg="#005500",fg="white",font=("Arial",12,"bold"))
        name_lbl.place(x=10,y=6)

        tot_lbl = tk.Label(frame,text="Total : ?",bg="#005500",fg="white",font=("Arial",11))
        tot_lbl.place(x=10,y=34)

        canvas = tk.Canvas(frame,width=280,height=110,bg="#005500",highlightthickness=0)
        canvas.place(x=10,y=58)
        # adjust player canvas height to match smaller card images
        canvas.config(height=130)

        res_lbl = tk.Label(frame,text="",bg="#005500",fg="yellow",font=("Arial",10,"bold"))
        res_lbl.place(x=10,y=190)

        hit_btn = tk.Button(frame,text="Hit",width=7)
        hit_btn.place(x=170,y=200)

        stand_btn = tk.Button(frame,text="Stand",width=7)
        stand_btn.place(x=230,y=200)

        player_frames.append(frame)
        player_canvases.append(canvas)
        player_total_labels.append(tot_lbl)
        player_name_labels.append(name_lbl)
        player_result_labels.append(res_lbl)
        player_hit_buttons.append(hit_btn)
        player_stand_buttons.append(stand_btn)

    # ---------- Deck ----------
    def new_deck():
        d = CARD_NAMES * 4
        random.shuffle(d)
        return d

    def card_value(c):
        if c in ("J","Q","K"): return 10
        if c=="AS": return 11
        return int(c)

    def hand_value(hand):
        t=0; aces=0
        for c in hand:
            if c=="AS": t+=11; aces+=1
            else: t+=card_value(c)
        while t>21 and aces>0:
            t-=10; aces-=1
        return t

    # ---------- UI Helpers ----------
    def draw_hand_on_canvas(canvas, hand):
        canvas.delete("all")
        canvas.image_refs=[]
        x=0
        for c in hand:
            img=card_images.get(c)
            canvas.image_refs.append(img)
            canvas.create_image(10+x,10,anchor="nw",image=img)
            x+=CARD_IMG_SIZE[0]-30

    def update_player_display(idx):
        if idx>=len(active_players):
            player_name_labels[idx].config(text=f"Slot {idx+1}")
            player_total_labels[idx].config(text="Total : ?")
            player_result_labels[idx].config(text="")
            player_canvases[idx].delete("all")
            return

        u = active_players[idx]
        st = player_states[u]
        player_name_labels[idx].config(text=u)
        draw_hand_on_canvas(player_canvases[idx], st['hand'])
        player_total_labels[idx].config(text=f"Total : {hand_value(st['hand'])}")

        if st['busted']: player_result_labels[idx].config(text="Bust")
        elif st['stood']: player_result_labels[idx].config(text="Stand")
        else: player_result_labels[idx].config(text="")

    def update_dealer_display(hide=True):
        dealer_canvas.delete("all")
        dealer_canvas.image_refs=[]
        x=10
        for i,c in enumerate(dealer_hand):
            if hide and i==1:
                back = ImageTk.PhotoImage(make_back_image())
                dealer_canvas.image_refs.append(back)
                dealer_canvas.create_image(x,10,anchor="nw",image=back)
            else:
                img = card_images[c]
                dealer_canvas.image_refs.append(img)
                dealer_canvas.create_image(x,10,anchor="nw",image=img)
            x+=CARD_IMG_SIZE[0]-40

        if hide:
            dealer_total_lbl.config(text="Total : ?")
        else:
            dealer_total_lbl.config(text=f"Total : {hand_value(dealer_hand)}")

    # ---------- Game Logic ----------
    def enable_controls():
        for idx,u in enumerate(active_players):
            st = player_states[u]
            if game_in_progress and not st['stood'] and not st['busted']:
                player_hit_buttons[idx].config(state="normal")
                player_stand_buttons[idx].config(state="normal")
            else:
                player_hit_buttons[idx].config(state="disabled")
                player_stand_buttons[idx].config(state="disabled")

    def disable_controls():
        for b in player_hit_buttons+player_stand_buttons:
            b.config(state="disabled")

    def deal_initial():
        nonlocal deck, dealer_hand, game_in_progress
        deck = new_deck()
        dealer_hand=[]
        for u in active_players:
            s=player_states[u]
            s['hand']=[]; s['stood']=False; s['busted']=False; s['result']=""

        for _ in range(2):
            for u in active_players:
                player_states[u]['hand'].append(deck.pop())
            dealer_hand.append(deck.pop())

        for i in range(MAX_PLAYERS):
            update_player_display(i)
        update_dealer_display(hide=True)
        enable_controls()

    def check_end():
        for u in active_players:
            s=player_states[u]
            if not (s['stood'] or s['busted']):
                return
        root.after(300, dealer_play)

    def dealer_play():
        nonlocal deck, dealer_hand, game_in_progress
        disable_controls()
        update_dealer_display(hide=False)

        while hand_value(dealer_hand)<17:
            if not deck: deck=new_deck()
            dealer_hand.append(deck.pop())
            update_dealer_display(hide=False)
            root.update()

        dv = hand_value(dealer_hand)
        for idx,u in enumerate(active_players):
            s=player_states[u]
            pv=hand_value(s['hand'])

            if s['busted']:
                res="Perdu"
            else:
                if dv>21:
                    res="Gagné"
                elif pv>dv:
                    res="Gagné"
                elif pv<dv:
                    res="Perdu"
                else:
                    res="Égalité"

            s['result']=f"{res}"
            player_result_labels[idx].config(text=s['result'])

        game_in_progress=False
        

    def hit(idx):
        nonlocal deck
        if idx>=len(active_players): return
        u=active_players[idx]
        s=player_states[u]
        if s['stood'] or s['busted'] or not game_in_progress:
            return
        if not deck: deck=new_deck()
        s['hand'].append(deck.pop())
        update_player_display(idx)
        if hand_value(s['hand'])>21:
            s['busted']=True
        enable_controls()
        check_end()

    def stand(idx):
        if idx>=len(active_players): return
        u=active_players[idx]
        s=player_states[u]
        s['stood']=True
        update_player_display(idx)
        enable_controls()
        check_end()

    # ---------- Buttons callbacks ----------
    for i in range(MAX_PLAYERS):
        player_hit_buttons[i].config(command=lambda i=i: hit(i))
        player_stand_buttons[i].config(command=lambda i=i: stand(i))

    def start_simple_game():
        nonlocal active_players, player_states, game_in_progress, deck, dealer_hand
        active_players=[f"Joueur {i+1}" for i in range(MAX_PLAYERS)]
        player_states={}

        for i,u in enumerate(active_players):
            player_states[u]={
                'hand':[],
                'stood':False,
                'busted':False,
                'result':""
            }

            # ⬇️ Ajout important : Réactiver les boutons AVANT la nouvelle main
            player_hit_buttons[i].config(state="normal")
            player_stand_buttons[i].config(state="normal")

            update_player_display(i)

        game_in_progress=True
        deck=[]
        dealer_hand=[]

        deal_initial()

        root.after(50, enable_controls)

       

    start_btn = tk.Button(root, text="Commencer une nouvelle partie",
                          command=start_simple_game,
                          bg="#00A86B",fg="white",width=25,height=2)
    start_btn.place(x=10,y=80)

 

   
    # Empty initial display
    for i in range(MAX_PLAYERS):
        update_player_display(i)

    root.mainloop()

# ---------------- Start program ----------------
if __name__ == "__main__":
    create_start_window()
