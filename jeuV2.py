import tkinter as tk
import random

# ------------------- CONSTANTES ------------------- #

TAILLE_GRILLE = 10
BATEAUX_A_PLACER = [5, 4, 3, 3, 2, 2]  # total 6 bateaux

VIDE = -1     # non découvert / vide
EAU = 0       # eau (tir raté)
TOUCHE = -2   # bateau touché

# ------------------- VARIABLES GLOBALES ------------------- #

root = None
nom_joueur = "Joueur"
difficulte = "Facile"
orientation_bateau = "H"
phase_de_placement = True

joueur_courant = "Joueur"
score_joueur = 0
score_ia = 0

# Grilles
grille_joueur = [[VIDE]*TAILLE_GRILLE for _ in range(TAILLE_GRILLE)]
grille_ia = [[VIDE]*TAILLE_GRILLE for _ in range(TAILLE_GRILLE)]

bateaux_joueur_restants = {}  # {bateau_id: nb_cases_restantes}
bateaux_ia_restants = {}      # {bateau_id: nb_cases_restantes}
tirs_reussis_ia = []          # liste de (i, j) déjà touchés par l'IA (mode difficile)

# Frames pour l’interface
frame_menu = None
frame_placement = None
frame_battle = None
frame_fin = None

label_infos = None
entry_nom_joueur = None
label_difficulte = None
difficulty_scale = None

# ------------------------------------------------ #
#              FONCTIONS D'INTERFACE              #
# ------------------------------------------------ #

def montrerFrameMenu():
    """Affiche le menu et masque les autres frames."""
    frame_menu.pack(fill="both", expand=True)
    frame_placement.pack_forget()
    frame_battle.pack_forget()
    frame_fin.pack_forget()

def montrerFramePlacement():
    """Affiche le frame de placement et met à jour la grille de placement."""
    frame_menu.pack_forget()
    frame_placement.pack(fill="both", expand=True)
    frame_battle.pack_forget()
    frame_fin.pack_forget()
    majAffichagePlacement()  # Important : affichage de la grille

def montrerFrameBattle():
    """Affiche le frame de bataille et met à jour la double grille (joueur/IA)."""
    frame_menu.pack_forget()
    frame_placement.pack_forget()
    frame_battle.pack(fill="both", expand=True)
    frame_fin.pack_forget()
    majAffichageBattle()  # Important : affichage des grilles de bataille

def montrerFrameFin():
    """Affiche le frame de fin (message de victoire/défaite, score, etc.)."""
    frame_menu.pack_forget()
    frame_placement.pack_forget()
    frame_battle.pack_forget()
    frame_fin.pack(fill="both", expand=True)

# ------------------------------------------------ #
#             FONCTIONS DE GESTION DU JEU          #
# ------------------------------------------------ #

def resetGame():
    """Réinitialise toutes les variables et revient au menu."""
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

    joueur_courant = nom_joueur
    phase_de_placement = True

    montrerFrameMenu()

def startGame():
    """
    Lance la phase de placement pour le joueur.
    Place aussi les bateaux de l'IA aléatoirement.
    """
    global nom_joueur, joueur_courant

    # Récupère le nom du joueur
    saisie = entry_nom_joueur.get().strip()
    if saisie:
        nom_joueur = saisie

    # Détermine la difficulté via le slider
    scale_val = difficulty_scale.get()
    if scale_val == 0:
        setDifficulte("Facile")
    else:
        setDifficulte("Difficile")

    # Placement aléatoire de l'IA
    genererPlacementAleatoire(grille_ia, bateaux_ia_restants)

    # On passe au placement du joueur
    joueur_courant = nom_joueur
    montrerFramePlacement()

def verifierFinPartie():
    """
    Vérifie si l'un des joueurs a un score de 6 (bateaux coulés).
    S'il y a un vainqueur, on appelle afficherMessageFin(...)
    """
    if score_joueur == 6:
        afficherMessageFin(f"{nom_joueur} a gagné la partie !")
        return True
    elif score_ia == 6:
        afficherMessageFin("L'IA a gagné la partie !")
        return True
    return False

def afficherMessageFin(message):
    """
    Affiche le message de fin sur frame_fin (même fenêtre), 
    propose de Rejouer ou Quitter.
    """
    for widget in frame_fin.winfo_children():
        widget.destroy()

    lbl_titre = tk.Label(frame_fin, text="Fin de la partie", 
                         font=("Helvetica", 20, "bold"), bg="#dfd")
    lbl_titre.pack(pady=15)

    lbl_message = tk.Label(frame_fin, text=message, font=("Helvetica", 14), bg="#dfd")
    lbl_message.pack(pady=10)

    lbl_score = tk.Label(frame_fin, 
                         text=f"Score {nom_joueur} : {score_joueur} | Score IA : {score_ia}",
                         font=("Helvetica", 12), bg="#dfd")
    lbl_score.pack(pady=5)

    # Boutons
    frame_btns = tk.Frame(frame_fin, bg="#dfd")
    frame_btns.pack(pady=20)

    btn_rejouer = tk.Button(frame_btns, text="Rejouer", command=resetGame, bg="#cfc")
    btn_rejouer.pack(side="left", padx=20)

    btn_quitter = tk.Button(frame_btns, text="Quitter", command=root.quit, bg="#fcc")
    btn_quitter.pack(side="left", padx=20)

    montrerFrameFin()

# ------------------------------------------------ #
#        FONCTIONS ANNEXES (PLACEMENT, TIRS...)    #
# ------------------------------------------------ #

def setDifficulte(diff):
    """Modifie la difficulté globale (Facile ou Difficile)."""
    global difficulte
    difficulte = diff

def genererPlacementAleatoire(grille, bateaux_restants):
    """
    Place les bateaux de façon aléatoire dans la grille.
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
                    # Vérifier que les cases sont libres
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

def changerOrientation():
    """Change l'orientation (Horizontale <-> Verticale) pour le placement."""
    global orientation_bateau
    orientation_bateau = "H" if orientation_bateau == "V" else "V"
    majAffichagePlacement()

def placerBateau(i, j):
    """
    Place le prochain bateau du joueur (en fonction de orientation_bateau)
    s’il reste des bateaux à placer.
    """
    global bateaux_joueur_restants
    nb_deja_places = len(bateaux_joueur_restants)
    if nb_deja_places >= len(BATEAUX_A_PLACER):
        return  # tous placés

    taille = BATEAUX_A_PLACER[nb_deja_places]
    bateau_id = nb_deja_places + 1

    if orientation_bateau == "H":
        if j + taille > TAILLE_GRILLE:
            return
        # Vérifie qu'on a la place vide
        for c in range(j, j + taille):
            if grille_joueur[i][c] != VIDE:
                return
        # On place
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

    # On stocke le bateau_id
    bateaux_joueur_restants[bateau_id] = taille
    majAffichagePlacement()

    # Si on a placé tous les bateaux
    if len(bateaux_joueur_restants) == len(BATEAUX_A_PLACER):
        lancerBattle()

def majAffichagePlacement():
    """Met à jour l'affichage de la grille du joueur pour le placement."""
    # On détruit les anciens widgets, sauf le label_infos
    for widget in frame_placement.winfo_children():
        if widget not in (label_infos,):
            widget.destroy()

    label_infos.config(text=f"Phase de placement pour {nom_joueur} :\n"
                            f"Orientation : {orientation_bateau}\n"
                            f"Bateaux placés : {len(bateaux_joueur_restants)}/{len(BATEAUX_A_PLACER)}")

    # Grille
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
    """Fin du placement, on passe à la phase de bataille."""
    global phase_de_placement, joueur_courant
    phase_de_placement = False
    joueur_courant = nom_joueur
    montrerFrameBattle()  # Affiche la bataille et majAffichageBattle()

def majAffichageBattle():
    """Affiche la grille du joueur et celle de l'IA."""
    for widget in frame_battle.winfo_children():
        widget.destroy()

    lbl_tour = tk.Label(frame_battle, 
                        text=f"C'est le tour de : {joueur_courant}",
                        font=("Helvetica", 14, "bold"), bg="#ddf")
    lbl_tour.pack(pady=5)

    frame_grilles = tk.Frame(frame_battle)
    frame_grilles.pack()

    # === Grille Joueur ===
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
                # Bateau encore vivant
                texte = str(val)
                couleur = "#bbbbbb"

            tk.Button(frame_gj, text=texte, width=2, height=1, bg=couleur,
                      state="disabled").grid(row=i, column=j, padx=1, pady=1)

    # === Grille IA ===
    frame_ia_local = tk.Frame(frame_grilles, bg="#fdd", bd=2, relief="groove")
    frame_ia_local.pack(side="left", padx=10)

    tk.Label(frame_ia_local, text="Grille Adverse (IA)", bg="#fdd",
             font=("Helvetica", 12, "underline")).pack(pady=5)

    frame_gi = tk.Frame(frame_ia_local, bg="#fdd")
    frame_gi.pack(pady=5)

    # Le joueur peut tirer seulement si c'est son tour
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
                # Non touché => on montre "~"
                texte = "~"
                couleur = "#ffffff"

            if can_shoot:
                btn = tk.Button(frame_gi, text=texte, width=2, height=1, bg=couleur,
                                command=lambda r=i, c=j: tirSurCase(r, c))
            else:
                btn = tk.Button(frame_gi, text=texte, width=2, height=1,
                                bg=couleur, state="disabled")

            btn.grid(row=i, column=j, padx=1, pady=1)

def tirSurCase(i, j):
    """Gère le tir du joueur sur la grille_ia."""
    global score_joueur, joueur_courant

    case_val = grille_ia[i][j]
    if case_val in (EAU, TOUCHE):
        # Déjà tiré ici
        return

    if case_val > 0:
        # Touché un bateau
        bateau_id = case_val
        grille_ia[i][j] = TOUCHE
        bateaux_ia_restants[bateau_id] -= 1

        if bateaux_ia_restants[bateau_id] == 0:
            score_joueur += 1

        if verifierFinPartie():
            # Affiche la fin
            majAffichageBattle()
            return

        # Le joueur rejoue
        majAffichageBattle()

    elif case_val == VIDE:
        # Dans l'eau
        grille_ia[i][j] = EAU
        # C'est au tour de l'IA
        joueur_courant = "IA"
        majAffichageBattle()
        # On laisse un délai avant le tour de l'IA
        root.after(1000, tourIA)

def tourIA():
    """Gère le tour de l'IA. Choix de la case en fonction de la difficulté."""
    global joueur_courant, score_ia

    if difficulte == "Facile":
        i, j = choisirTirAleatoireIA()
    else:
        i, j = choisirTirDifficileIA()

    case_val = grille_joueur[i][j]
    if case_val in (EAU, TOUCHE):
        # Déjà tiré, retenter immédiatement
        tourIA()
        return

    if case_val > 0:
        # Touché un bateau du joueur
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
    """Retourne un (i, j) aléatoire non déjà tiré (EAU ou TOUCHE)."""
    while True:
        i = random.randint(0, TAILLE_GRILLE - 1)
        j = random.randint(0, TAILLE_GRILLE - 1)
        if grille_joueur[i][j] not in (EAU, TOUCHE):
            return i, j

def choisirTirDifficileIA():
    """L'IA cherche autour d'une case déjà touchée pour retoucher un bateau."""
    if tirs_reussis_ia:
        i0, j0 = random.choice(tirs_reussis_ia)
        autour = [(i0-1, j0), (i0+1, j0), (i0, j0-1), (i0, j0+1)]
        random.shuffle(autour)
        for (ii, jj) in autour:
            if 0 <= ii < TAILLE_GRILLE and 0 <= jj < TAILLE_GRILLE:
                if grille_joueur[ii][jj] not in (EAU, TOUCHE):
                    return (ii, jj)
    return choisirTirAleatoireIA()

# ------------------------------------------------ #
#              CRÉATION DE L'INTERFACE             #
# ------------------------------------------------ #

def majLabelDifficulte(val):
    """Met à jour le label de difficulté (Facile ou Difficile) en temps réel."""
    if float(val) == 0:
        label_difficulte.config(text="Facile")
    else:
        label_difficulte.config(text="Difficile")

def creerInterface():
    """
    Crée tous les frames (menu, placement, battle, fin) 
    et configure la fenêtre.
    """
    global root
    global frame_menu, frame_placement, frame_battle, frame_fin
    global label_infos, entry_nom_joueur, label_difficulte, difficulty_scale

    root = tk.Tk()
    root.title("Bataille Navale - Version tout-en-un")
    root.geometry("800x600")
    root.config(bg="#ffffff")

    # ----- Frame Menu ----- #
    frame_menu = tk.Frame(root, bg="#ccf")

    label_titre = tk.Label(frame_menu, text="Bataille Navale", 
                           font=("Helvetica", 20, "bold"), bg="#ccf")
    label_titre.pack(pady=20)

    tk.Label(frame_menu, text="Entrez votre nom :", bg="#ccf").pack()
    entry_nom_joueur = tk.Entry(frame_menu, width=20)
    entry_nom_joueur.pack(pady=5)

    # Slider pour la difficulté (0=Facile, 1=Difficile)
    tk.Label(frame_menu, text="Choisissez la difficulté (2 positions) :", bg="#ccf").pack(pady=5)
    
    label_difficulte = tk.Label(frame_menu, text="Facile", bg="#ccf", font=("Helvetica", 12, "bold"))
    label_difficulte.pack(pady=2)

    difficulty_scale = tk.Scale(frame_menu, from_=0, to=1, resolution=1, 
                                orient='horizontal', length=200,
                                bg="#ccf", command=majLabelDifficulte)
    difficulty_scale.set(0)
    difficulty_scale.pack(pady=5)

    tk.Button(frame_menu, text="Commencer la partie", bg="#cdf", command=startGame).pack(pady=30)

    # ----- Frame Placement ----- #
    frame_placement = tk.Frame(root, bg="#dde")

    label_infos = tk.Label(frame_placement, text="", bg="#dde", font=("Helvetica", 12))
    label_infos.pack(pady=10)

    # ----- Frame Battle ----- #
    frame_battle = tk.Frame(root, bg="#eee")

    # ----- Frame Fin ----- #
    frame_fin = tk.Frame(root, bg="#dfd")

    # On affiche le menu par défaut au lancement
    montrerFrameMenu()

    return root

# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    root = creerInterface()
    root.mainloop()
