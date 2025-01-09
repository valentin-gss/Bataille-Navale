import tkinter as tk
import random

# ------------------- CONSTANTES ------------------- #

TAILLE_GRILLE = 10
BATEAUX_A_PLACER = [5, 4, 3, 3, 2, 2]  # total 6 bateaux

VIDE = -1    # non découvert / vide
EAU = 0      # eau (tir raté)
TOUCHE = -2  # bateau touché

# ------------------- VARIABLES GLOBALES ------------------- #

root = None             # Fenêtre principale
nom_joueur = "Joueur"   # Nom du joueur (par défaut, modifié via l'Entry)
difficulte = "Facile"   # Par défaut (choisi via le slider)
orientation_bateau = "H"
phase_de_placement = True

joueur_courant = "Joueur"
score_joueur = 0
score_ia = 0

# Grilles
grille_joueur = [[VIDE]*TAILLE_GRILLE for _ in range(TAILLE_GRILLE)]
grille_ia = [[VIDE]*TAILLE_GRILLE for _ in range(TAILLE_GRILLE)]

bateaux_joueur_restants = {}
bateaux_ia_restants = {}
tirs_reussis_ia = []

# Frames pour l’interface
frame_menu = None
frame_placement = None
frame_battle = None
label_infos = None
entry_nom_joueur = None
difficulty_scale = None


# ------------------- FONCTIONS D'AIDE ------------------- #

def genererPlacementAleatoire(grille, bateaux_restants):
    """
    Place les bateaux de façon aléatoire dans la grille (pour l'IA).
    Mise à jour du dict bateaux_restants : {bateau_id: nb_cases_restantes}.
    """
    bateau_id = 1
    for taille in BATEAUX_A_PLACER:
        place = False
        while not place:
            orient = random.choice(["H", "V"])
            i = random.randint(0, TAILLE_GRILLE - 1)
            j = random.randint(0, TAILLE_GRILLE - 1)

            if orient == "H":
                if j + taille <= TAILLE_GRILLE:
                    if all(grille[i][c] == VIDE for c in range(j, j + taille)):
                        for c in range(j, j + taille):
                            grille[i][c] = bateau_id
                        place = True
            else:  # "V"
                if i + taille <= TAILLE_GRILLE:
                    if all(grille[r][j] == VIDE for r in range(i, i + taille)):
                        for r in range(i, i + taille):
                            grille[r][j] = bateau_id
                        place = True

        bateaux_restants[bateau_id] = taille
        bateau_id += 1


def verifierFinPartie():
    """
    Vérifie si l'un des joueurs a un score de 6 (tous les bateaux coulés).
    """
    global score_joueur, score_ia
    if score_joueur == 6:
        afficherMessageFin(f"{nom_joueur} a gagné la partie !")
        return True
    elif score_ia == 6:
        afficherMessageFin("L'IA a gagné la partie !")
        return True
    return False


def afficherMessageFin(message):
    """
    Affiche un message de fin et propose de Rejouer ou Quitter.
    """
    fen_fin = tk.Toplevel(root)
    fen_fin.title("Fin de la partie")

    lbl = tk.Label(fen_fin, text=message, font=("Helvetica", 14, "bold"))
    lbl.pack(pady=10)

    lbl_score = tk.Label(fen_fin, text=f"Score {nom_joueur} : {score_joueur} - Score IA : {score_ia}")
    lbl_score.pack(pady=5)

    def rejouer():
        fen_fin.destroy()
        resetGame()

    def quitter():
        root.quit()

    btn_rejouer = tk.Button(fen_fin, text="Rejouer", command=rejouer, bg="#cfc")
    btn_rejouer.pack(side="left", padx=20, pady=10)

    btn_quitter = tk.Button(fen_fin, text="Quitter", command=quitter, bg="#fcc")
    btn_quitter.pack(side="right", padx=20, pady=10)


# ------------------- FONCTIONS DE GESTION DU JEU ------------------- #

def resetGame():
    """
    Réinitialise toutes les variables et revient au menu.
    """
    global grille_joueur, grille_ia, score_joueur, score_ia
    global bateaux_joueur_restants, bateaux_ia_restants, tirs_reussis_ia
    global joueur_courant, phase_de_placement

    grille_joueur = [[VIDE]*TAILLE_GRILLE for _ in range(TAILLE_GRILLE)]
    grille_ia = [[VIDE]*TAILLE_GRILLE for _ in range(TAILLE_GRILLE)]

    score_joueur = 0
    score_ia = 0
    bateaux_joueur_restants = {}
    bateaux_ia_restants = {}
    tirs_reussis_ia = []

    # On remet le joueur_courant au nom du joueur
    joueur_courant = nom_joueur
    phase_de_placement = True

    # On revient au menu
    montrerFrameMenu()


def montrerFrameMenu():
    frame_menu.pack(fill="both", expand=True)
    frame_placement.pack_forget()
    frame_battle.pack_forget()


def montrerFramePlacement():
    frame_menu.pack_forget()
    frame_placement.pack(fill="both", expand=True)
    frame_battle.pack_forget()
    majAffichagePlacement()


def montrerFrameBattle():
    frame_menu.pack_forget()
    frame_placement.pack_forget()
    frame_battle.pack(fill="both", expand=True)
    majAffichageBattle()


def startGame():
    """
    Lance la phase de placement pour le joueur.
    Place aussi les bateaux de l'IA aléatoirement.
    Récupère le nom du joueur depuis l'Entry du menu, et fixe joueur_courant.
    """
    global nom_joueur, joueur_courant

    # Récupère le nom du joueur
    saisie = entry_nom_joueur.get().strip()
    if saisie != "":
        nom_joueur = saisie

    # Mécanisme du slider : si < 0.5 => Facile, sinon => Difficile
    scale_val = difficulty_scale.get()
    if scale_val < 0.5:
        difficulte_str = "Facile"
    else:
        difficulte_str = "Difficile"

    # On assigne la difficulté
    setDifficulte(difficulte_str)

    # On place l’IA
    genererPlacementAleatoire(grille_ia, bateaux_ia_restants)

    # Le joueur commence à placer
    joueur_courant = nom_joueur
    montrerFramePlacement()


# ------------------- FONCTIONS DE PLACEMENT ------------------- #

def changerOrientation():
    global orientation_bateau
    if orientation_bateau == "H":
        orientation_bateau = "V"
    else:
        orientation_bateau = "H"
    majAffichagePlacement()


def placerBateau(i, j):
    global bateaux_joueur_restants

    nb_deja_places = len(bateaux_joueur_restants)
    if nb_deja_places >= len(BATEAUX_A_PLACER):
        return  # tous placés

    taille = BATEAUX_A_PLACER[nb_deja_places]
    bateau_id = nb_deja_places + 1

    if orientation_bateau == "H":
        if j + taille > TAILLE_GRILLE:
            return
        for c in range(j, j + taille):
            if grille_joueur[i][c] != VIDE:
                return
        for c in range(j, j + taille):
            grille_joueur[i][c] = bateau_id
    else:  # "V"
        if i + taille > TAILLE_GRILLE:
            return
        for r in range(i, i + taille):
            if grille_joueur[r][j] != VIDE:
                return
        for r in range(i, i + taille):
            grille_joueur[r][j] = bateau_id

    bateaux_joueur_restants[bateau_id] = taille
    majAffichagePlacement()

    if len(bateaux_joueur_restants) == len(BATEAUX_A_PLACER):
        lancerBattle()


def majAffichagePlacement():
    """
    Met à jour l'affichage de la grille pour la phase de placement.
    """
    for widget in frame_placement.winfo_children():
        if widget not in (label_infos, ):
            widget.destroy()

    label_infos.config(text=f"Phase de placement pour {nom_joueur} :\n"
                            f"Orientation : {orientation_bateau}\n"
                            f"Bateaux placés : {len(bateaux_joueur_restants)}/{len(BATEAUX_A_PLACER)}")

    # Frame pour la grille
    frame_grid = tk.Frame(frame_placement, bg="#ddddff")
    frame_grid.pack(pady=10)

    for i in range(TAILLE_GRILLE):
        for j in range(TAILLE_GRILLE):
            val = grille_joueur[i][j]
            if val == VIDE:
                texte = ""
                couleur = "#ffffff"
            else:
                texte = str(val)
                couleur = "#bbbbbb"

            bouton = tk.Button(frame_grid, text=texte, width=2, height=1,
                               bg=couleur,
                               command=lambda r=i, c=j: placerBateau(r, c))
            bouton.grid(row=i, column=j, padx=1, pady=1)

    btn_orient = tk.Button(frame_placement, text="Changer orientation (H/V)",
                           command=changerOrientation, bg="#eef")
    btn_orient.pack(pady=5)


def lancerBattle():
    global phase_de_placement, joueur_courant
    phase_de_placement = False
    joueur_courant = nom_joueur
    montrerFrameBattle()


# ------------------- FONCTIONS DE BATAILLE ------------------- #

def majAffichageBattle():
    for widget in frame_battle.winfo_children():
        widget.destroy()

    lbl_tour = tk.Label(frame_battle, 
                        text=f"C'est le tour de : {joueur_courant}",
                        font=("Helvetica", 14, "bold"), bg="#ddf")
    lbl_tour.pack(pady=5)

    frame_grilles = tk.Frame(frame_battle)
    frame_grilles.pack()

    # --- Grille Joueur ---
    frame_joueur_local = tk.Frame(frame_grilles, bg="#ddf", bd=2, relief="groove")
    frame_joueur_local.pack(side="left", padx=10)

    tk.Label(frame_joueur_local, text=f"Grille de {nom_joueur}", bg="#ddf",
             font=("Helvetica", 12, "underline")).pack(pady=5)

    frame_gj = tk.Frame(frame_joueur_local, bg="#ddf")
    frame_gj.pack(pady=5)

    for i in range(TAILLE_GRILLE):
        for j in range(TAILLE_GRILLE):
            val = grille_joueur[i][j]
            if val == VIDE:
                texte = "~"
                couleur = "#ffffff"
            elif val == EAU:
                texte = "•"
                couleur = "#99ccff"
            elif val == TOUCHE:
                texte = "X"
                couleur = "#ff6666"
            else:
                texte = str(val)
                couleur = "#bbbbbb"

            tk.Button(frame_gj, text=texte, width=2, height=1, bg=couleur,
                      state="disabled").grid(row=i, column=j, padx=1, pady=1)

    # --- Grille IA ---
    frame_ia_local = tk.Frame(frame_grilles, bg="#fdd", bd=2, relief="groove")
    frame_ia_local.pack(side="left", padx=10)

    tk.Label(frame_ia_local, text="Grille Adverse (IA)", bg="#fdd",
             font=("Helvetica", 12, "underline")).pack(pady=5)

    frame_gi = tk.Frame(frame_ia_local, bg="#fdd")
    frame_gi.pack(pady=5)

    can_shoot = (joueur_courant == nom_joueur)

    for i in range(TAILLE_GRILLE):
        for j in range(TAILLE_GRILLE):
            val = grille_ia[i][j]
            if val == EAU:
                texte = "•"
                couleur = "#99ccff"
            elif val == TOUCHE:
                texte = "X"
                couleur = "#ff6666"
            else:
                texte = "~"
                couleur = "#ffffff"

            if can_shoot:
                btn = tk.Button(frame_gi, text=texte, width=2, height=1,
                                bg=couleur,
                                command=lambda r=i, c=j: tirSurCase(r, c))
            else:
                btn = tk.Button(frame_gi, text=texte, width=2, height=1,
                                bg=couleur, state="disabled")
            btn.grid(row=i, column=j, padx=1, pady=1)


def tirSurCase(i, j):
    global score_joueur, joueur_courant

    case_val = grille_ia[i][j]
    if case_val in (EAU, TOUCHE):
        return  # déjà tiré

    if case_val > 0:
        # Touché un bateau
        bateau_id = case_val
        grille_ia[i][j] = TOUCHE
        bateaux_ia_restants[bateau_id] -= 1
        if bateaux_ia_restants[bateau_id] == 0:
            score_joueur += 1

        if verifierFinPartie():
            majAffichageBattle()
            return

        # Le joueur (nom_joueur) rejoue
        majAffichageBattle()

    elif case_val == VIDE:
        # Eau
        grille_ia[i][j] = EAU
        # Passe à l'IA
        joueur_courant = "IA"
        majAffichageBattle()
        root.after(1000, tourIA)


def tourIA():
    global joueur_courant, score_ia

    if difficulte == "Facile":
        i, j = choisirTirAleatoireIA()
    else:
        i, j = choisirTirDifficileIA()

    case_val = grille_joueur[i][j]
    if case_val in (EAU, TOUCHE):
        # déjà tiré, réessayer tout de suite
        tourIA()
        return

    if case_val > 0:
        # Touché
        bateau_id = case_val
        grille_joueur[i][j] = TOUCHE
        bateaux_joueur_restants[bateau_id] -= 1

        if (i, j) not in tirs_reussis_ia:
            tirs_reussis_ia.append((i, j))

        if bateaux_joueur_restants[bateau_id] == 0:
            score_ia += 1

        if verifierFinPartie():
            majAffichageBattle()
            return

        # IA rejoue
        majAffichageBattle()
        root.after(600, tourIA)

    else:
        # Eau
        grille_joueur[i][j] = EAU
        joueur_courant = nom_joueur
        majAffichageBattle()


def choisirTirAleatoireIA():
    while True:
        i = random.randint(0, TAILLE_GRILLE - 1)
        j = random.randint(0, TAILLE_GRILLE - 1)
        if grille_joueur[i][j] not in (EAU, TOUCHE):
            return i, j


def choisirTirDifficileIA():
    if tirs_reussis_ia:
        i0, j0 = random.choice(tirs_reussis_ia)
        autour = [(i0-1, j0), (i0+1, j0), (i0, j0-1), (i0, j0+1)]
        random.shuffle(autour)
        for (ii, jj) in autour:
            if 0 <= ii < TAILLE_GRILLE and 0 <= jj < TAILLE_GRILLE:
                if grille_joueur[ii][jj] not in (EAU, TOUCHE):
                    return (ii, jj)

    return choisirTirAleatoireIA()


# ------------------- FONCTIONS LIEES A LA DIFFICULTÉ ------------------- #

def setDifficulte(diff):
    global difficulte
    difficulte = diff


# ------------------- CRÉATION DE L'INTERFACE ------------------- #

def creerInterface():
    """
    Crée la fenêtre principale et les 3 frames : menu, placement, battle.
    Ajoute un Entry pour le nom du joueur et un Scale pour la difficulté.
    """
    global root, frame_menu, frame_placement, frame_battle
    global label_infos, entry_nom_joueur, difficulty_scale

    root = tk.Tk()
    root.title("Bataille Navale (Version Joueur + Slider)")
    root.geometry("800x600")
    root.config(bg="#ffffff")

    # ----- Frame Menu ----- #
    frame_menu = tk.Frame(root, bg="#ccf")

    label_titre = tk.Label(frame_menu, text="Bataille Navale", font=("Helvetica", 20, "bold"), bg="#ccf")
    label_titre.pack(pady=20)

    # Zone de saisie du nom du joueur
    tk.Label(frame_menu, text="Entrez votre nom :", bg="#ccf").pack()
    entry_nom_joueur = tk.Entry(frame_menu, width=20)
    entry_nom_joueur.pack(pady=5)

    # Slider pour choisir la difficulté (0 = Facile, 1 = Difficile)
    tk.Label(frame_menu, text="Choisissez la difficulté (glisser) :", bg="#ccf").pack(pady=5)
    difficulty_scale = tk.Scale(frame_menu, from_=0, to=1, orient='horizontal',
                                resolution=0.01, length=200, bg="#ccf")
    difficulty_scale.pack(pady=5)

    # Bouton pour commencer la partie
    tk.Button(frame_menu, text="Commencer la partie", bg="#cdf", command=startGame).pack(pady=30)

    # ----- Frame Placement ----- #
    frame_placement = tk.Frame(root, bg="#dde")

    label_infos = tk.Label(frame_placement, text="", bg="#dde", font=("Helvetica", 12))
    label_infos.pack(pady=10)
    # Le reste de la grille est généré dans majAffichagePlacement()

    # ----- Frame Battle ----- #
    frame_battle = tk.Frame(root, bg="#eee")

    # Affiche par défaut le menu
    montrerFrameMenu()

    return root


# ------------------- MAIN ------------------- #

if __name__ == "__main__":
    root = creerInterface()
    root.mainloop()
