import tkinter as tk
import random

# ------------------- CONSTANTES ------------------- #

TAILLE_GRILLE = 10
BATEAUX_A_PLACER = [5, 4, 3, 3, 2, 2]  # total 6 bateaux

# -1 = non découvert, 0 = eau, >0 = partie d'un bateau, -2 = bateau touché
VIDE = -1
EAU = 0
TOUCHE = -2

# ------------------- VARIABLES GLOBALES ------------------- #

root = None  # Fenêtre principale

difficulte = "Facile"      # Valeur par défaut de la difficulté
orientation_bateau = "H"   # Orientation par défaut (Horizontal)
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
            # Orientation aléatoire
            orient = random.choice(["H", "V"])
            i = random.randint(0, TAILLE_GRILLE - 1)
            j = random.randint(0, TAILLE_GRILLE - 1)

            if orient == "H":
                if j + taille <= TAILLE_GRILLE:
                    # Vérifier si les cases sont libres (VIDE)
                    if all(grille[i][c] == VIDE for c in range(j, j + taille)):
                        # Placer le bateau
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
        afficherMessageFin("Le Joueur a gagné !")
        return True
    elif score_ia == 6:
        afficherMessageFin("L'IA a gagné !")
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

    lbl_score = tk.Label(fen_fin, text=f"Score Joueur : {score_joueur} - Score IA : {score_ia}")
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


# ------------------- FONCTIONS DE JEU ------------------- #

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

    joueur_courant = "Joueur"
    phase_de_placement = True

    # On revient au menu
    montrerFrameMenu()


def montrerFrameMenu():
    """
    Affiche le menu (et masque les autres frames).
    """
    frame_menu.pack(fill="both", expand=True)
    frame_placement.pack_forget()
    frame_battle.pack_forget()


def montrerFramePlacement():
    """
    Affiche la phase de placement (et masque les autres frames).
    """
    frame_menu.pack_forget()
    frame_placement.pack(fill="both", expand=True)
    frame_battle.pack_forget()
    majAffichagePlacement()


def montrerFrameBattle():
    """
    Affiche la phase de bataille (et masque les autres frames).
    """
    frame_menu.pack_forget()
    frame_placement.pack_forget()
    frame_battle.pack(fill="both", expand=True)
    majAffichageBattle()


def startGame():
    """
    Lance la phase de placement pour le joueur.
    Place aussi les bateaux de l'IA aléatoirement.
    """
    genererPlacementAleatoire(grille_ia, bateaux_ia_restants)
    montrerFramePlacement()


# ------------------- PHASE DE PLACEMENT ------------------- #

def changerOrientation():
    """
    Bascule entre Horizontal (H) et Vertical (V) pour placer les bateaux.
    """
    global orientation_bateau
    if orientation_bateau == "H":
        orientation_bateau = "V"
    else:
        orientation_bateau = "H"
    majAffichagePlacement()


def placerBateau(i, j):
    """
    Place le bateau suivant (en fonction de l'orientation_bateau) si possible.
    """
    global bateaux_joueur_restants

    # Combien de bateaux déjà placés ?
    nb_deja_places = len(bateaux_joueur_restants)
    if nb_deja_places >= len(BATEAUX_A_PLACER):
        return  # tous placés

    taille = BATEAUX_A_PLACER[nb_deja_places]
    bateau_id = nb_deja_places + 1

    # Vérifier si ça rentre
    if orientation_bateau == "H":
        if j + taille > TAILLE_GRILLE:
            return
        # Vérifier si toutes les cases sont libres
        for c in range(j, j + taille):
            if grille_joueur[i][c] != VIDE:
                return
        # Placer
        for c in range(j, j + taille):
            grille_joueur[i][c] = bateau_id
    else:  # "V"
        if i + taille > TAILLE_GRILLE:
            return
        for r in range(i, i + taille):
            if grille_joueur[r][j] != VIDE:
                return
        # Placer
        for r in range(i, i + taille):
            grille_joueur[r][j] = bateau_id

    # Stocker le bateau
    bateaux_joueur_restants[bateau_id] = taille

    majAffichagePlacement()

    # Si tous les bateaux sont placés, on passe à la bataille
    if len(bateaux_joueur_restants) == len(BATEAUX_A_PLACER):
        lancerBattle()


def majAffichagePlacement():
    """
    Met à jour l'affichage de la grille pour la phase de placement.
    """
    # On vide le frame_placement (sauf la barre du haut)
    for widget in frame_placement.winfo_children():
        if widget not in (label_infos, ):
            widget.destroy()

    label_infos.config(text="Phase de placement : Cliquez sur une case pour placer le prochain bateau.\n"
                            f"Orientation actuelle : {orientation_bateau}\n"
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

    # Bouton pour changer l'orientation
    btn_orient = tk.Button(frame_placement, text="Changer orientation (H/V)",
                           command=changerOrientation, bg="#eef")
    btn_orient.pack(pady=5)


def lancerBattle():
    """
    Prépare l’affichage et lance la phase de bataille.
    """
    global phase_de_placement, joueur_courant
    phase_de_placement = False
    joueur_courant = "Joueur"
    montrerFrameBattle()


# ------------------- PHASE DE BATAILLE ------------------- #

def majAffichageBattle():
    """
    Met à jour l’affichage des deux grilles (joueur + adversaire)
    et affiche le joueur_courant.
    """
    # On vide tout le contenu de frame_battle
    for widget in frame_battle.winfo_children():
        widget.destroy()

    lbl_tour = tk.Label(frame_battle, text=f"C'est le tour de : {joueur_courant}",
                        font=("Helvetica", 14, "bold"), bg="#ddf")
    lbl_tour.pack(pady=5)

    # Frame globale qui contient la grille Joueur + grille IA
    frame_grilles = tk.Frame(frame_battle)
    frame_grilles.pack()

    # --- Grille Joueur ---
    frame_joueur_local = tk.Frame(frame_grilles, bg="#ddf", bd=2, relief="groove")
    frame_joueur_local.pack(side="left", padx=10)

    tk.Label(frame_joueur_local, text="Votre grille", bg="#ddf",
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
                texte = "•"  # petit rond pour loupé
                couleur = "#99ccff"
            elif val == TOUCHE:
                texte = "X"
                couleur = "#ff6666"
            else:
                # Bateau intact
                texte = str(val)
                couleur = "#bbbbbb"

            tk.Button(frame_gj, text=texte, width=2, height=1, bg=couleur,
                      state="disabled").grid(row=i, column=j, padx=1, pady=1)

    # --- Grille IA ---
    frame_ia_local = tk.Frame(frame_grilles, bg="#fdd", bd=2, relief="groove")
    frame_ia_local.pack(side="left", padx=10)

    tk.Label(frame_ia_local, text="Grille Adverse", bg="#fdd",
             font=("Helvetica", 12, "underline")).pack(pady=5)

    frame_gi = tk.Frame(frame_ia_local, bg="#fdd")
    frame_gi.pack(pady=5)

    # Le joueur ne peut tirer que si c’est son tour
    can_shoot = (joueur_courant == "Joueur")

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
                # Bateau ou vide, on ne dévoile pas où est le bateau de l'IA
                # tant que ce n'est pas touché
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
    """
    Gère le tir du joueur sur la grille_ia (i, j).
    """
    global score_joueur, joueur_courant

    case_val = grille_ia[i][j]
    if case_val == EAU or case_val == TOUCHE:
        # déjà tiré ici
        return

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

        # Le joueur rejoue
        majAffichageBattle()

    elif case_val == VIDE:
        # Dans l'eau
        grille_ia[i][j] = EAU
        # On passe à l'IA
        joueur_courant = "IA"
        majAffichageBattle()
        root.after(1000, tourIA)  # l’IA joue après 1s environ


def tourIA():
    """
    Gère le tour de l'IA. Choix de la case en fonction de la difficulté.
    """
    global joueur_courant, score_ia

    if difficulte == "Facile":
        i, j = choisirTirAleatoireIA()
    else:
        i, j = choisirTirDifficileIA()

    # Vérif et exécution du tir
    case_val = grille_joueur[i][j]
    if case_val == EAU or case_val == TOUCHE:
        # déjà tiré
        tourIA()  # On retente immédiatement (sinon IA peut boucler si malchance)
        return

    if case_val > 0:
        # Touché un bateau du joueur
        bateau_id = case_val
        grille_joueur[i][j] = TOUCHE
        bateaux_joueur_restants[bateau_id] -= 1
        # On ajoute ce tir réussi à la liste
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
        # Dans l'eau
        grille_joueur[i][j] = EAU
        joueur_courant = "Joueur"
        # On actualise l'affichage
        majAffichageBattle()


def choisirTirAleatoireIA():
    """
    Retourne un (i, j) au hasard non encore tiré par l'IA.
    """
    while True:
        i = random.randint(0, TAILLE_GRILLE - 1)
        j = random.randint(0, TAILLE_GRILLE - 1)
        if grille_joueur[i][j] not in (EAU, TOUCHE):
            return i, j


def choisirTirDifficileIA():
    """
    IA "intelligente" : si elle a touché un bateau récemment,
    essaye de tirer autour ; sinon aléatoire.
    """
    # Cherche d'abord dans tirs_reussis_ia
    if tirs_reussis_ia:
        # On prend au hasard une case touchée
        i0, j0 = random.choice(tirs_reussis_ia)
        # On liste les positions autour
        autour = [(i0-1, j0), (i0+1, j0), (i0, j0-1), (i0, j0+1)]
        random.shuffle(autour)
        for (ii, jj) in autour:
            if 0 <= ii < TAILLE_GRILLE and 0 <= jj < TAILLE_GRILLE:
                if grille_joueur[ii][jj] not in (EAU, TOUCHE):
                    return (ii, jj)

    # Sinon on tire au hasard
    return choisirTirAleatoireIA()


# ------------------- CREATION DE L'INTERFACE ------------------- #

def creerInterface():
    """
    Crée la fenêtre principale et les 3 frames : menu, placement, battle.
    """
    global root, frame_menu, frame_placement, frame_battle, label_infos

    root = tk.Tk()
    root.title("Bataille Navale (Version Débutant)")
    root.geometry("800x600")
    root.config(bg="#ffffff")

    # ----- Frame Menu ----- #
    frame_menu = tk.Frame(root, bg="#ccf")

    label_titre = tk.Label(frame_menu, text="Bataille Navale", font=("Helvetica", 20, "bold"), bg="#ccf")
    label_titre.pack(pady=20)

    def setDifficulteFacile():
        global difficulte
        difficulte = "Facile"

    def setDifficulteDifficile():
        global difficulte
        difficulte = "Difficile"

    tk.Label(frame_menu, text="Choisissez la difficulté :", bg="#ccf").pack(pady=5)
    frame_btns = tk.Frame(frame_menu, bg="#ccf")
    frame_btns.pack(pady=5)
    tk.Button(frame_btns, text="Facile", bg="#efe", command=setDifficulteFacile).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Difficile", bg="#fee", command=setDifficulteDifficile).pack(side="left", padx=5)

    tk.Button(frame_menu, text="Commencer la partie", bg="#cdf", command=startGame).pack(pady=30)

    # ----- Frame Placement ----- #
    frame_placement = tk.Frame(root, bg="#dde")

    label_infos = tk.Label(frame_placement, text="", bg="#dde", font=("Helvetica", 12))
    label_infos.pack(pady=10)

    # Le reste de la grille est généré dans majAffichagePlacement()

    # ----- Frame Battle ----- #
    frame_battle = tk.Frame(root, bg="#eee")

    # On affiche par défaut le menu
    montrerFrameMenu()

    return root


# ------------------- MAIN ------------------- #
if __name__ == "__main__":
    root = creerInterface()
    root.mainloop()
