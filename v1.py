import tkinter as tk
import random

def demarrer_jeu():
    menu_frame.pack_forget()  # Masquer le menu principal
    jeu_frame.pack()  # Afficher le jeu

def clique_joueur(x, y):
    global tour
    if tour == "joueur":
        bouton = ordi_plateau[x][y]
        if bouton["bg"] == "gray":
            bouton.config(bg="red", state=tk.DISABLED)
            tour = "ordi"
            label_tour.config(text="Tour : Ordinateur")
            fenetre.after(1000, tour_ordinateur)

def tour_ordinateur():
    global tour
    while True:
        x = random.randint(0, 9)
        y = random.randint(0, 9)
        bouton = joueur_plateau[x][y]
        if bouton["bg"] == "blue":
            bouton.config(bg="red", state=tk.DISABLED)
            break
    tour = "joueur"
    label_tour.config(text="Tour : Joueur")

# Fenêtre principale
fenetre = tk.Tk()
fenetre.title("Bataille Navale")

# Menu principal
menu_frame = tk.Frame(fenetre)
menu_frame.pack()

tk.Label(menu_frame, text="Bataille Navale", font=("Arial", 20, "bold")).pack(pady=20)

tk.Label(menu_frame, text="Choisissez la difficulté", font=("Arial", 14)).pack(pady=10)
difficulte = tk.StringVar(value="Facile")
curseur_difficulte = tk.Scale(menu_frame, from_=0, to=1, orient=tk.HORIZONTAL, showvalue=0,
                              label="Facile    |    Difficile", length=200, variable=difficulte)
curseur_difficulte.pack(pady=10)

bouton_demarrer = tk.Button(menu_frame, text="Démarrer le jeu", command=demarrer_jeu, font=("Arial", 14))
bouton_demarrer.pack(pady=20)

# Jeu principal
jeu_frame = tk.Frame(fenetre)

# Plateau joueur
joueur_frame = tk.Frame(jeu_frame)
joueur_frame.pack(side=tk.LEFT, padx=10)
joueur_plateau = [[None for _ in range(10)] for _ in range(10)]
tk.Label(joueur_frame, text="Votre grille", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=10)

for i in range(10):
    for j in range(10):
        bouton = tk.Button(joueur_frame, width=4, height=2, bg="blue", state=tk.NORMAL)
        bouton.grid(row=i+1, column=j)
        joueur_plateau[i][j] = bouton

# Plateau ordinateur
ordi_frame = tk.Frame(jeu_frame)
ordi_frame.pack(side=tk.RIGHT, padx=10)
ordi_plateau = [[None for _ in range(10)] for _ in range(10)]
tk.Label(ordi_frame, text="Grille adversaire", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=10)

for i in range(10):
    for j in range(10):
        bouton = tk.Button(ordi_frame, width=4, height=2, bg="gray", command=lambda x=i, y=j: clique_joueur(x, y))
        bouton.grid(row=i+1, column=j)
        ordi_plateau[i][j] = bouton

# Indicateur de tour
label_tour = tk.Label(jeu_frame, text="Votre tour", font=("Arial", 16, "bold"))
label_tour.pack()

# Variables globales
tour = "joueur"

# Lancer l'application
fenetre.mainloop()
