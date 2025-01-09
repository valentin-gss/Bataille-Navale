import tkinter as tk
import random

# Variables globales (initialisées plus loin)
fenetre = None
menu_frame = None
jeu_frame = None
label_tour = None
joueur_plateau = []
ordi_plateau = []
tour = "joueur"


def clique_joueur(x, y):
    global tour
    # Coup du joueur
    if tour == "joueur":
        bouton = ordi_plateau[x][y]
        if bouton["bg"] == "gray":
            bouton.config(bg="red", state=tk.DISABLED)
            tour = "ordi"
            label_tour.config(text="Tour actuel : Ordinateur")
            fenetre.after(1000, tour_ordinateur)

def tour_ordinateur():
    global tour
    # Coup de l'ordinateur
    while True:
        x = random.randint(0, 9)
        y = random.randint(0, 9)
        bouton = joueur_plateau[x][y]
        if bouton["bg"] == "blue":
            bouton.config(bg="red", state=tk.DISABLED)
            break
    tour = "joueur"
    label_tour.config(text="Tour actuel : Joueur")

def demarrer_jeu():
    """Masquer le menu et afficher la grille de jeu."""
    menu_frame.pack_forget()   # On masque le menu
    # On crée puis on affiche le jeu
    create_game_frame()
    jeu_frame.pack(fill=tk.BOTH, expand=True)

def create_game_frame():
    """Crée la frame de jeu et les deux grilles (joueur et ordinateur)."""
    global jeu_frame, label_tour, joueur_plateau, ordi_plateau

    # --- Frame principale du jeu ---
    jeu_frame = tk.Frame(fenetre, bg="#ADD8E6")

    label_tour = tk.Label(
        jeu_frame, 
        text="Tour actuel : Joueur", 
        font=("Arial", 16, "bold"),
        fg="#000000",
        bg="#ADD8E6"
    )
    label_tour.pack(pady=10)

    # Container des deux grilles
    grilles_container = tk.Frame(jeu_frame, bg="#ADD8E6")
    grilles_container.pack(pady=10)

    # --- Plateau Joueur ---
    joueur_frame = tk.Frame(grilles_container, bg="#ADD8E6")
    joueur_frame.pack(side=tk.LEFT, padx=30)

    titre_joueur = tk.Label(
        joueur_frame, 
        text="Votre grille", 
        font=("Arial", 14, "bold"),
        bg="#ADD8E6", 
        fg="#000000"
    )
    titre_joueur.grid(row=0, column=0, columnspan=10, pady=5)

    joueur_plateau = [[None for _ in range(10)] for _ in range(10)]

    # Pour avoir un effet "carré", utilisez une police monospacée (Courier) 
    # et ajustez width/height.
    button_font = ("Courier", 14, "bold")

    for i in range(10):
        for j in range(10):
            bouton = tk.Button(
                joueur_frame,
                width=2,         # Largeur en caractères (monospacés)
                height=1,        # Hauteur en lignes
                bg="blue", 
                fg="white",
                activebackground="darkblue",
                font=button_font,
                bd=2,
                relief=tk.RIDGE,
                state=tk.NORMAL
            )
            bouton.grid(row=i+1, column=j, padx=1, pady=1)
            joueur_plateau[i][j] = bouton

    # --- Plateau Ordinateur ---
    ordi_frame = tk.Frame(grilles_container, bg="#ADD8E6")
    ordi_frame.pack(side=tk.RIGHT, padx=30)

    titre_ordi = tk.Label(
        ordi_frame, 
        text="Grille adversaire", 
        font=("Arial", 14, "bold"), 
        bg="#ADD8E6", 
        fg="#000000"
    )
    titre_ordi.grid(row=0, column=0, columnspan=10, pady=5)

    ordi_plateau = [[None for _ in range(10)] for _ in range(10)]

    for i in range(10):
        for j in range(10):
            bouton = tk.Button(
                ordi_frame,
                width=2,
                height=1,
                bg="gray", 
                fg="white",
                activebackground="red",
                font=button_font,
                bd=2,
                relief=tk.RIDGE,
                command=lambda x=i, y=j: clique_joueur(x, y)
            )
            bouton.grid(row=i+1, column=j, padx=1, pady=1)
            ordi_plateau[i][j] = bouton

    # On réaffecte nos plateaux globaux pour y accéder dans tour_ordinateur()
    globals()["joueur_plateau"] = joueur_plateau
    globals()["ordi_plateau"] = ordi_plateau


# -----------------------------------------------------------------------------
#                      Programme principal
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # --- Fenêtre principale ---
    fenetre = tk.Tk()
    fenetre.title("Bataille Navale")
    fenetre.geometry("850x600")
    fenetre.resizable(False, False)
    fenetre.configure(bg="#ADD8E6")  # Fond bleu clair

    # --- Menu principal (affiché au démarrage) ---
    menu_frame = tk.Frame(fenetre, bg="#ADD8E6")
    menu_frame.pack(fill=tk.BOTH, expand=True)

    titre_label = tk.Label(
        menu_frame, 
        text="Bataille Navale", 
        font=("Arial", 28, "bold"), 
        fg="white", 
        bg="#ADD8E6"
    )
    titre_label.pack(pady=30)

    instruction_label = tk.Label(
        menu_frame, 
        text="Choisissez la difficulté", 
        font=("Arial", 16, "bold"),
        fg="#333333", 
        bg="#ADD8E6"
    )
    instruction_label.pack(pady=10)

    difficulte = tk.StringVar(value="Facile")
    curseur_difficulte = tk.Scale(
        menu_frame, 
        from_=0, to=1, 
        orient=tk.HORIZONTAL, 
        showvalue=0,
        label="Facile    |    Difficile", 
        length=300, 
        variable=difficulte,
        font=("Arial", 12, "bold"),
        bg="#ADD8E6",
        fg="#333333",
        troughcolor="white",
        activebackground="#87CEEB",
        highlightthickness=0
    )
    curseur_difficulte.pack(pady=10)

    bouton_demarrer = tk.Button(
        menu_frame, 
        text="Démarrer le jeu", 
        command=demarrer_jeu, 
        font=("Arial", 16, "bold"),
        bg="#1E90FF", 
        fg="white",
        activebackground="#4682B4",
        bd=3,
        relief=tk.RAISED
    )
    bouton_demarrer.pack(pady=40)

    # --- Lancement de la boucle principale ---
    fenetre.mainloop()
