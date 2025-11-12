# Lance l’application Tkinter (fenêtre principale)
from tkinter import *

# --- Fenêtre principale ---
window = Tk()
window.title("Roulette Casino")
window.geometry("400x400")
window.resizable(False, False)

# --- Fond image pour se connecter ou creer un compte ---
bg_image = PhotoImage(file="Fond_Casino")

window.mainloop()