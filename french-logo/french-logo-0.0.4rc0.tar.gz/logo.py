#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
#
#  logo.py
#
#  Copyright 2019 Robert Sebille <robert@sebille.name>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import turtle
from random import randint


class Tortue(turtle.Turtle):

    # Special methods, used in setup.py
    @staticmethod
    def version():
        """
        Retourne la version de la classe.

        Attention, le numero de version du setup.py est extrait d'ici.
        """
        print("Version 0.0.4rc")
    # version = classmethod(version)

    ####################
    # Class attributes #
    ####################

    monnom = ""
    """Attribut de classe. Nom à qui s'adressera le système.

    Si vide, ce sera 'Monsieur',
    'Monseigneur', 'Madame', 'Messire', 'Sire', 'Majesté', 'Excellence', ou
    'Emminence' au hasard."""

    compte = 0
    ecran = None

    _chefs = (
        "Monsieur",
        "Monseigneur",
        "Madame",
        "Messire",
        "Sire",
        "Majesté",
        "Excellence",
        "Emminence",
    )

    _obeissances = (
        "à vos ordres, ",
        "à votre service, ",
        "j'attends vos instructions, ",
        "j'attends vos souhaits, ",
        "en attente de vos instructions, ",
        "en attente de vos ordres, ",
        "sous votre commandement, ",
        "à votre disposition, ",
    )

    _formes = {
        "flèche":    "arrow",
        "rien":      "blank",
        "cercle":    "circle",
        "classique": "classic",
        "carré":     "square",
        "triangle":  "triangle",
        "tortue":    "turtle",
    }
    # Dictionnaire des formes de la tortue

    _vitesses = {
        "très lente":       "slowest",
        "lente":            "slow",
        "normale":          "normal",
        "rapide":           "fast",
        "en avant toute":   "fastest",
    }
    # Dictionnaire des vitesses de la tortue

    _couleurs = {
        "blanc clair":      "lightwhite",
        "blanc":            "white",
        "blanc foncé":      "darkwhite",

        "bleu clair":       "lightblue",
        "bleu":             "blue",
        "bleu foncé":       "darkblue",

        "brun clair":       "lightbrown",
        "brun":             "brown",
        "brun foncé":       "darkbrown",

        "gris clair":       "lightgrey",
        "gris":             "grey",
        "gris foncé":       "darkgrey",

        "jaune clair":      "lightyellow",
        "jaune":            "yellow",
        "jaune foncé":      "darkyellow",

        "noir clair":       "lightblack",
        "noir":             "black",
        "noir foncé":       "darkblack",

        "orange clair":     "lightorange",
        "orange":           "orange",
        "orange foncé":     "darkorange",

        "rose clair":       "lightpink",
        "rose":             "pink",
        "rose foncé":       "darkpink",

        # "rouge clair":      "lightred",
        # problème inconnu avec ligthred
        "rouge clair":      "red",
        "rouge":            "red",
        "rouge foncé":      "darkred",

        "vert clair":       "lightgreen",
        "vert":             "green",
        "vert foncé":       "darkgreen",

        "violet clair":     "lightpurple",
        "violet":           "purple",
        "violet foncé":     "darkpurple",
    }
    # Dictionnaire des couleurs de la tortue

    # liste_fonctions = ("mt", "montretortue", "ct", "cachetortue", "avance",
    # "recule", "av", "re", "tournegauche", "tg", "tournedroite", "td",
    # "debut_remplissage", "fin_remplissage")

    ################
    # Constructeur #
    ################

    def __init__(self):
        """Consructeur

        La classe Tortue retourne un substitut de primitives logo en français,
        basées sur le module turtle Elle comporte également une primitive
        repete récursive (absente du module turtle)

        Les primitives distance(), position() et pos() sont identiques
        en français et en anglais et donc non traduites

        - position(), pos(): retourne la position courante (x, y) de la tortue
        - distance(): retourne la distance de la tortue a (x, y) ou à une \
        autre tortue. Paramètres:

            :param x: -- un nombre, une paire de nombre ou une instance tortue
            :param y: -- un nombre si x est un nombre, sinon None

        la primitive distance() est particulièrement utile avec la primitive
        vers(). Exemple:

    .. code-block::

         # la tortue t1 rejoint la tortue t2
         t1.cap = t1.vers(t2)
         t1.av(distance(t2))

    .. note::
        l'instruction **'repete' n'accepte que des variables Tortue**.
        D'où le besoin de disposer de telles variables pour obtenir des \
        variations de paramètres. Historiquement, la tortue dispose de \
        3 variables attachées à son service v1 = 0, v2 = 0 et v3 = 0. Mais, \
        c'est limitatif d'une part, et, d'autre part, il est très aisé \
        d'ajouter à une classe des variables "à la volée". Exemple :\
        Tortue.var0 = 0 ou <objet_tortue>.var0 = 0;
        """
        # class Turtle
        turtle.Turtle.__init__(self)  # Constructeur classe mère

        # class Tortue
        self.no_tortue = "Tortue n°" + str(Tortue.compte + 1)

        self._initialise()

        # class Screen
        if Tortue.compte == 0:
            Tortue.ecran = self.screen
            # evitons de renvoyer toutes les tortues à 0,0 lors de
            # la création d'une tortue
            Tortue.fixe_mode_ecran("logo")
            Tortue.ecran.colormode(255)
            Tortue.fixe_titre_ecran("Bienvenue dans le zoo aux tortues !")
            Tortue.monnom = Tortue._chefs[randint(0, len(Tortue._chefs) - 1)]
        self.penup()
        Tortue.compte += 1

    ############
    # Privates #
    ############

    def _initialise(self):
        # class Turtle
        self.showturtle()
        self.speed("slowest")
        self.shape(Tortue._formes["tortue"])
        self.penup()

        # class Tortue
        self._visible = True
        self._forme = "tortue"
        self._cap = 0.0
        self._crayonbaisse = False
        self._largeurcrayon = 1
        self._couleur = "noir", "noir"
        self._remplis = False
        self._vitesse = "très lente"

        self.v1 = 0
        self.v2 = 0
        self.v3 = 0

    ###############
    # __special__ #
    ###############

    def __str__(self):
        tortue = self.no_tortue + ' sur ' + str(Tortue.compte) + '. x, y: ' +\
            str(round(self.coordx(), 2)) + ", " + str(round(self.coordy(), 2))\
            + '. Cap: ' + str(self._cap) + '. Vitesse: ' + self.vitesse + \
            "\nCouleur crayon: " + str(self.couleur[0]) + ", remplissage: " +\
            str(self.couleur[1]) + ". Crayon baissé: " + \
            str(self.crayonbaisse) + ".\n" + "Taille crayon: " + \
            str(self.largeurcrayon) + "px. Visible ? " + str(self.visible) +\
            ". Forme: " + self.forme + "\n" + self.no_tortue + ", " + \
            Tortue._obeissances[randint(0, len(Tortue._obeissances) - 1)] + \
            Tortue.monnom + " !"
        return tortue

    ##########################
    # Class methods (screen) #
    ##########################
    def au_revoir_ecran(cls, message="", clic=False):
        """Ferme la fenêtre tortue, puis affiche 'message' à la console.
        Si 'clic'=True, attends qu'on clique sur l'écran pour le fermer.
        Défaut pour clic = False"""
        if clic:
            cls.ecran.exitonclick()
        else:
            cls.ecran.bye()
        print(message)
    au_revoir_ecran = classmethod(au_revoir_ecran)

    def configure_ecran(cls, largeur, hauteur, posx, posy):
        """Fixe les dimensions et la position de l'écran, suivant les
        paramètres ci-dessous.

        :param largeur: largeur de l'écran en px (défaut = 50% de l'écran)
        :param hauteur: hauteur de l'écran en px (défaut = 75% de l'écran)
        :param posx: position écran en x; positif = à partir du bord gauche, \
                     négatif = à partir du bord droit
        :param posy: position écran en y; positif = à partir du bord haut, \
                     négatif = à partir du bord bas
        """
        cls.ecran.setup(largeur, hauteur, posx, posy)
    configure_ecran = classmethod(configure_ecran)

    def ecran_attends(cls, millisecondes):
        """Le programme attend 'millisecondes' millisecondes"""
        cls.ecran.delay(millisecondes)
    ecran_attends = classmethod(ecran_attends)

    def fixe_mode_ecran(cls, mode):
        """Fixe le mode de l'écran

        - "logo": angles et orientation géographique (Défaut)
        - "standard": angles et orientation trigonométrique
        """
        cls.ecran.mode(mode)
    fixe_mode_ecran = classmethod(fixe_mode_ecran)

    def dit_mode_ecran(cls):
        """Retourne le mode de l'écran"""
        return cls.ecran.mode()
    dit_mode_ecran = classmethod(dit_mode_ecran)

    def fixe_titre_ecran(cls, titre):
        """Fixe le titre de l'écran"""
        cls.ecran.title(titre)
    fixe_titre_ecran = classmethod(fixe_titre_ecran)

    def lis_texte_ecran(cls, titre, invite):
        """Fournit une fenêtre de dialogue et de saise d'un texte. Renvoie
        le texte. Supporte un titre et une invite."""
        return cls.ecran.textinput(titre, invite)
    lis_texte_ecran = classmethod(lis_texte_ecran)

    def lis_nombre_ecran(cls, titre, invite, defaut=None, minimum=None,
                         maximum=None):
        """Fournit une fenêtre de dialogue et de saise d'un nombre. Renvoie
        le nombre.
        Paramètres obligatoires

        :param titre: titre
        :param invite: invite

        Paramètres optionnels

        :param defaut: valeur par défaut
        :param minimum: valeur minimum d'entrée
        :param maximum: valeur maximum d'entrée
        """
        return cls.ecran.numinput(titre, invite, defaut, minimum, maximum)
    lis_nombre_ecran = classmethod(lis_nombre_ecran)

    def lis_formes(cls):
        """retourne le dictionnaire des formes tortue disponibles"""
        return cls._formes
    lis_formes = classmethod(lis_formes)

    def lis_couleurs(cls):
        """retourne le dictionnaire des couleurs tortue disponibles"""
        return cls._couleurs
    lis_couleurs = classmethod(lis_couleurs)

    def lis_vitesses(cls):
        """retourne le dictionnaire des vitesses tortue disponibles"""
        return cls._vitesses
    lis_vitesses = classmethod(lis_vitesses)

    ##############
    # properties #
    ##############
    def get_cap(self):
        return self._cap

    def set_cap(self, cap):
        self.setheading(cap)
        self._cap = cap

    cap = property(get_cap, set_cap, "",
                   """Fixe, modifie ou retourne le cap de la tortue.
    Le cap est fonction du mode:

    - "logo": angles et orientation géographique
    - "standard": angles et orientation trigonométrique (Défaut)
    """)

    def get_couleur(self):
        return self._couleur

    def set_couleur(self, *args):
        fillpen = args[0]
        p = fillpen[0]
        f = self._couleur[1] if len(fillpen) < 2 else fillpen[1]
        self.color(Tortue._couleurs[p], Tortue._couleurs[f])
        self._couleur = p, f

    couleur = property(get_couleur, set_couleur, "",
                       """
    Fixe, modifie ou retourne les couleurs du crayon et de remplissage.
    usage: <objet_tortue>.couleur = (couleur_crayon,[couleur_remplissage"])

    Couleurs disponibles: 'blanc', 'bleu', 'brun', 'gris', 'jaune', 'noir',
    'orange', 'rose', 'rouge', 'vert', 'violet
    Chaque couleur est disponible en 3 tons: clair, normal, foncé

    Exemples:

    .. code-block::

        t = Tortue()
        t.couleur = 'bleu foncé', 'rouge'
        t.couleur = 'vert clair', # <- NE PAS OUBLIER LA ',' car il s'agit
        # d'un tuple !

    .. warning::
            Il y a un problème avec "rouge clair" actuellement qui est redirigé
            automatiquement le "rouge" normal.
    """)

    def get_crayonbaisse(self):
        return self._crayonbaisse

    crayonbaisse = property(get_crayonbaisse, "", "",
                            """
        Retourne True/False, si le crayon est baissé ou pas.""")

    def get_forme(self):
        return self._forme

    def set_forme(self, forme):
        self.shape(Tortue._formes[forme])
        self._forme = forme

    forme = property(get_forme, set_forme, "",
                     """
    Fixe, modifie ou retourne la forme de la tortue.

    Formes disponibles: 'carré', 'cercle', 'classique', 'flèche', 'tortue',
    'triangle', 'rien'
    """)

    def get_largeurcrayon(self):
        return self._largeurcrayon

    largeurcrayon = property(get_largeurcrayon, "", "",
                             """
    Retourne la taille du crayon de la tortue.""")

    def get_remplis(self):
        return self._remplis

    remplis = property(get_remplis, "", "",
                       """Retourne True/False, si la tortue est en mode
    remplissage ou pas.""")

    def get_visible(self):
        return self._visible

    visible = property(get_visible, "", "",
                       """Retourne True/False, si la tortue est visible
    ou pas.""")

    def get_vitesse(self):
        return self._vitesse

    def set_vitesse(self, vitesse):
        self.speed(Tortue._vitesses[vitesse])
        self._vitesse = vitesse

    vitesse = property(get_vitesse, set_vitesse, "",
                       """
    Fixe, modifie ou retourne la vitesse de la tortue.

    Vitesses disponibles: 'très lente', 'lente', 'normale', 'rapide',
    'en avant toute'
    """)

    #################################
    # Dictionnaires, listes, etc... #
    #################################

    ###################
    # Publics methods #
    ###################
    #########
    # Etats #
    def mt(self):
        """Montre tortue"""
        self.showturtle()
        # pas de set_visible,
        # donc on appelle l'attribut privé _visibble directement
        self._visible = True

    def montretortue(self):
        """Montre tortue"""
        self.showturtle()
        self._visible = True

    def ct(self):
        """Cache tortue"""
        self.hideturtle()
        self._visible = False

    def cachetortue(self):
        """Cache tortue"""
        self.hideturtle()
        self._visible = False

    def bc(self):
        """Baisse le crayon de la tortue"""
        self.pd()
        self._crayonbaisse = True

    def baissecrayon(self):
        """Baisse le crayon de la tortue"""
        self.pendown()
        self._crayonbaisse = True

    def lc(self):
        """Lève le crayon de la tortue"""
        self.pu()
        self._crayonbaisse = False

    def levecrayon(self):
        """Lève le crayon de la tortue"""
        self.penup()
        self._crayonbaisse = False

    def tc(self, taille):
        """Lève le crayon de la tortue"""
        self.pensize(taille)
        self._largeurcrayon = taille

    def taillecrayon(self, taille):
        """Lève le crayon de la tortue"""
        self.pensize(taille)
        self._largeurcrayon = taille

    def coordx(self):
        """Retourne la position x de la tortue."""
        return self.xcor()

    def coordy(self):
        """Retourne la position y de la tortue."""
        return self.ycor()

    def cx(self):
        """Retourne la position x de la tortue."""
        return self.xcor()

    def cy(self):
        """Retourne la position y de la tortue."""
        return self.ycor()

    def vers(self, x, y=None):
        """Retourne l'angle entre la ligne de la position tortue, et (x, y)
        ou d'une autre tortue. Paramètres:

        :param x: -- un nombre, une paire de nombre ou une instance tortue
        :param y: -- un nombre si x est un nombre, sinon None
        """
        return self.towards(x, y)

    ##############
    # Mouvements #
    def avance(self, pas):
        """tortue avance de 'pas' """
        self.forward(pas)

    def recule(self, pas):
        """tortue recule de 'pas' """
        self.backward(pas)

    def av(self, pas):
        """tortue avance de 'pas' """
        self.forward(pas)

    def re(self, pas):
        """tortue recule de 'pas' """
        self.backward(pas)

    def va(self, x, y):
        """tortue va en 'x', 'y' """
        self.goto(x, y)

    def tournegauche(self, degres):
        """tortue tourne à gauche de 'degrés' """
        self.left(degres)
        self.cap = self.heading()

    def tournedroite(self, degres):
        """tortue tourne à droite de 'degrés' """
        self.right(degres)
        self.cap = self.heading()

    def tg(self, degres):
        """tortue tourne à gauche de 'degrés' """
        self.left(degres)
        self.cap = self.heading()

    def td(self, degres):
        """tortue tourne à droite de 'degrés' """
        self.right(degres)
        self.cap = self.heading()

    #############
    # fonctions #
    def cachet(self):
        """Laisse un cachet de forme tortue sur l'écran. Retourne un
        'id_cachet' qui peut être utilisé pour supprimer le cachet avec
        tortue.efface_cachet(id_cachet)

        Exemple:

    .. code-block::

        t = Tortue()
        cecachet = t.cachet()
        t.fd(50)
        t.efface_cachet(cecachet)

        """
        return self.stamp()

    def efface_cachet(self, id_cachet):
        """Supprime le cachet id_cachet. Voir la doc 'cachet()'."""
        self.clearstamp(id_cachet)

    def efface_cachets(self, n=None):
        """Si n > 0, supprime les n premiers cachets de tortue, sinon les n
        derniers. Si n=None, supprime tous les cachets de tortue.
        Voir la doc 'cachet()'."""
        self.clearstamps(n)

    def double(self):
        """Crée et retourne un double de la tortue, même position, même cap,
        mêmes propriétés.

        Exemple:

    .. code-block::

        robert = Tortue()
        anais = robert.double()

        """
        return self.clone()

    def clown(self):
        """Alias comique pour 'double()'"""
        return self.double()

    def efface(self):
        """Efface tous les dessins de la tortue. Laisse tous les
        autres états tels qu'ils sont"""
        self.clear()

    def reinitialise(self):
        """Efface tous les dessins de la tortue. Réinitialise toutes les
        variables de la tortue, comme  x, y = 0, 0 et cap = 0, par exemple"""
        self.reset()
        self._initialise()

    def maison(self):
        """Ramène la tortue à x, y = 0, 0 et cap = 0"""
        self.home()
        self.cap = 0

    def polycercle(self, rayon, arc=None, cote=None):
        """
    Dessine un polygone de rayon 'rayon', arc = 'arc', par défaut 360, et
    d'un nombre de cotés 'cote". A partir d'un nombre suffisant de cotés,
    le polygone apparait comme un cercle, c'est pourquoi nous l'appelons
    'polycercle' dans la suite

    Paramètres

        :param rayon: un nombre rayon fixant le cantre du polycercle\
        à gauche de la tortue. Si rayon est positif, le polycercle sera\
        dessiné dans le sens contre-horlogique, sinon horlogique
        :param arc: un nombre, arc de polycercle (Défaut = None)
        :param cote: nombre de cotés du polycercle (Defaut = None)\
        dans le cas d'un cercle, mieux vaut laisser la fonction décider\
        de ce paramètre.

        """
        self.circle(rayon, arc, cote)

    def pc(self, rayon, arc=None, cote=None):
        """Alias de polycercle"""
        self.circle(rayon, arc, cote)

    def debut_remplissage(self):
        """A appeler juste avant de dessiner une forme à remplir."""
        self.begin_fill()
        # pas de set_remplis,
        # donc on appelle l'attribut privé _visibble directement
        self._remplis = True

    def fin_remplissage(self):
        """Remplit la forme dessinée après le dernier appel à
        debut_remplissage()."""
        self.end_fill()
        # pas de set_remplis,
        # donc on appelle l'attribut privé _visibble directement
        self._remplis = False

    def ecris(self, message, bouge=False, aligne="left",
              fonte=("Arial", 8, "normal")):
        """Ecris un texte à l'écran
        Paramètres

        :param message: Message à écrire sur l'écran.
        :param bouge: True/False. Si True, la tortue est déplacée vers \
        le coin inférieur droit du texte.
        :param aligne: au choix: "left", "center" ou right"
        :param fonte: Un triplet description de la fonte (nom, taille, type)
        """
        self.write(message, bouge, aligne, fonte)

    # Cette fonction n'existe pas dans turtle.
    def repete(self, fois, liste):
        """
        Instruction absente de turtle, elle répete n fois une série de
        commandes. 'repete' est récursive, et donc, supporte d'autres
        'repete' à l'intérieur d'elle-même.

        Exemple d'usage:

        .. code-block::

            t = Tortue()
            t.repete(4, ["av(100", "td(90)"])
            t.repete(4, ["repete", 4, ["av(90)", "td(90)"], "td(90)"])

        Règles:

        1. l'instruction **'repete' n'accepte que des variables Tortue**.
        D'où le besoin de disposer de telles variables pour obtenir des \
        variations de paramètres. Historiquement, la tortue dispose de \
        3 variables attachées à son service v1 = 0, v2 = 0 et v3 = 0. Mais, \
        c'est limitatif d'une part, et, d'autre part, il est très aisé \
        d'ajouter à une classe des variables "à la volée". Exemple :\
        Tortue.var0 = 0 ou <objet_tortue>.var0 = 0; ... C'est cette methode \
        (dont nous aurons besoin) que nous choisirons pour la suite.

        2. **les instructions s'écrivent toutes entre guillemets**, simples \
        ou doubles, dans une liste et donc separées par des virgules.

        3. **si l'instruction Tortue débute**, elle s'écrit **telle quelle**, \
        **sinon**, elle doit être **précédée de self**. Exemple:\
        ["td(90)", "av(self.var0)"]

        4. **l'instruction est récursive** et peut se rapeller autant de \
        fois qu'on veut à l'intérieur, sur le modèle suivant: \
        t.repete(n, ["inst", "repete", n, ["inst", "etc."], "inst", "etc."])

        Notes à propos de la récursivité:

        - Le 1er appel à repete se construit comme \
        't.repete(n, ["..."])', l'appel récursif comme \
        '[ ... "repete", n, ["..."]]'. Seul n, le nombre de répétion \
        est un entier sans guillemet!

        - La récursivité est consommatrice de ressources, suggestion donc \
        de modérer le nombre d'appel récursif à 2 ou 3 (même si le nombre \
        maximum d'appels récursifs est 996 !).

        Astuce! comment introduire une fonction dans une boucle repete ?

        .. code-block:: python

            t1 = Tortue()
            def ballon(baton, rayon):
                t1.av(baton)
                t1.polycercle(rayon)
                t1.re(baton)

            def ballons(baton, rayon):
                t1.var0 = ballon
                t1.var1 = baton
                t1.var2 = rayon
                # Suivons la règle: "si l'instruction Tortue débute, elle
                # s'écrit telle quelle, sinon, elle est précédée de self."
                t1.repete(8, ["var0(self.var1, self.var2)", "tg(360/8)"])

            ballons(100, 50)

        """
        for i in range(fois):
            # element + while et pas for element, car on doit gérer element
            # (ce qui n'est pas possible avec for)
            element = 0
            while element < len(liste):
                inst = str(liste[element].strip())
                # print(inst)
                # si l'instruction est repete, on "récurse"
                if inst == "repete":
                    tmp = element
                    self.repete(liste[element+1], liste[element+2])
                    element = tmp + (len(liste[element+2]) + 1)
                else:
                    exec("self." + inst)
                    element += 1

    # To do ###
    # def pour(...):
        # pass
