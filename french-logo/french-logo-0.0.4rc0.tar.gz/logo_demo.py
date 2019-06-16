#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

from logo import Tortue

# Pour logo version 0.0.3alpha et +


# Utilitaires
def passe():
    Tortue.lis_texte_ecran("Pour continuer ...", "... pressez entrée !")
    pass


def delai(t, delai):
    Tortue.ecran_attends(delai)
    t.td(0)
    Tortue.ecran_attends(0)


def messages(t, titre, message, efface=False):
    t.couleur = ("blanc",) if efface else ("noir",)
    t.cap = 0
    t.va(0, 250)
    t.ecris(titre, False, "center", ("arial", "12", "bold"))
    t.cap = 180
    t.va(0, -250)
    t.ecris(message, False, "center", ("arial", "10", "normal"))


# Evenements 1
def elementaire():
    t2.va(100, 100)
    t3.va(-100, -100)
    t2.tg(90)
    t3.td(90)
    t2.couleur = 'bleu', 'rouge'
    t3.couleur = 'vert', 'jaune'
    t2.bc()
    t3.bc()
    t2.debut_remplissage()
    t3.debut_remplissage()
    t2.av(200)
    t2.tg(90)
    t2.av(200)
    t3.av(200)
    t3.tg(90)
    t3.av(200)
    t2.fin_remplissage()
    t3.fin_remplissage()
    t2.ecris(t2, False, "right")
    t3.ecris(t3)


# Evenement 2a
def polyetcerclea():
    t2.va(100, 100)
    t3.va(-100, -100)
    t2.bc()
    t3.cap = 180
    t3.bc()

    t3.polycercle(-30, None, 25)
    t3.couleur = "bleu", "jaune"
    t3.debut_remplissage()
    t3.pc(30)
    t3.fin_remplissage()

    t2.couleur = "violet", "rose"
    t2.debut_remplissage()
    t2.pc(50, 180)
    t2.fin_remplissage()
    t2.pc(-30, 270)


# Evenement 2b
def polyetcercleb():
    t2.va(100, 100)
    t3.va(-100, -100)
    t2.bc()
    t3.cap = 180
    t3.bc()

    t3.polycercle(-50, None, 3)
    t3.couleur = "bleu", "jaune"
    t3.tg(90)
    t3.lc()
    t3.av(200)
    t3.td(90)
    t3.bc()
    t3.debut_remplissage()
    t3.pc(50, None, 4)
    t3.fin_remplissage()

    t2.polycercle(-50, None, 5)
    t2.couleur = "violet", "rose"
    t2.tg(90)
    t2.lc()
    t2.av(200)
    t2.td(90)
    t2.bc()
    t2.debut_remplissage()
    t2.pc(50, None, 6)
    t2.fin_remplissage()

    t3.lc()
    t3.va(50, 0)
    t3.bc()
    t3.couleur = "noir", "noir"
    t3.pc(-50, None, 12)


# Evenement 2c
def distvers():
    t3.couleur = "rouge clair",

    t3.va(100, 50)
    t2.va(-100, -100)

    t3.ecris("Distance t3/t2 = " + str(t3.distance(t2)) + ". Cap = " +
             str(t3.vers(t2)), False, "center")

    t3.bc()
    t3.cap = t3.towards(t2)
    t3.av(t3.distance(t2))


# Evenement 2d
def copyclown():
    t2.va(-100, -100)
    t3.va(100, -100)
    t2.av(40)
    t3.av(40)
    t2.forme = "classique"
    t3.forme = "triangle"
    t2.repete(3, ["forme = 'classique'", "cachet()", "forme = 'tortue'",
              "av(40)"])
    t3.repete(3, ["forme = 'triangle'", "cachet()", "forme = 'tortue'",
              "av(40)"])
    passe()
    t2.efface_cachets(-2)
    t3.efface_cachets()
    passe()
    t3.forme = "flèche"
    t4 = t3.double()
    t4.va(0, 150)
    t3.ecris("Je suis t3", False, "center")
    t4.ecris("je suis t4, un double de t3", False, "center")
    t3.av(10)
    t4.av(10)
    passe()
    t4.reinitialise()
    t4.ct()


# Evenement 3a
def instrepete():
    t2.va(100, 100)
    t3.va(-100, -100)
    t2.bc()
    t3.cap = 180
    t3.bc()

    t3.couleur = "bleu", "jaune"
    t3.v1 = 10
    t3.repete(9, ["v1+=10", "repete", 4, ["av(self.v1)", "tg(90)"], "td(10)"])

    t2.couleur = "violet", "rose"
    t2.couleur = "bleu", "vert clair"
    t2.repete(4, ["debut_remplissage()", "repete", 4, ["av(90)", "td(90)"],
              "fin_remplissage()", "td(90)"])


# Evenement 4
def rosaces():
    t2.lc()
    t3.lc()
    t2.va(125, 90)
    t3.va(-130, -120)
    t2.bc()
    t3.bc()
    t2.couleur = "bleu", "rouge clair"
    t3.couleur = "rouge", "bleu"
    t2.vitesse = "en avant toute"
    t3.vitesse = "en avant toute"
    t2.ct()
    t3.ct()

    petit_cote = ["avance(30)", "tournedroite(90)"]
    grand_cote_et_petit_carre = ["av(100)", "td(90)", "repete", 4, petit_cote]
    var2 = ["tg(10)", "repete", 4, grand_cote_et_petit_carre]
    t2.debut_remplissage()
    t2.repete(36, var2)
    t2.fin_remplissage()
    t2.mt()
    t2.cap = 10
    t2.lc()
    t2.re(250)
    t2.cap = 0
    t2.ecris(t2, False, "left")

    t3.v1 = 0
    t3.debut_remplissage()
    t3.repete(36, [
                    "td(10)", "v1+=2", "repete", 4, [
                        "av(25 + self.v1)", "td(90)", "repete", 4, [
                            "av(self.v1/3)", "td(90)"]
                        ]
                    ])
    t3.fin_remplissage()
    t3.mt()
    t3.cap = 190
    t3.lc()
    t3.re(200)
    t3.cap = 180
    t3.ecris(t3, False, "right")


def demo():
    global t1
    global t2
    global t3

    # Création tortue
    t1 = Tortue()  # impression des messages
    t2 = Tortue()
    t3 = Tortue()

    # mon nom système
    Tortue.monnom = "Asmodée"

    Tortue.configure_ecran(900, 600, 200, 100)

    t1.ct()
    t1.va(0, 20)
    t1.ecris("Démonstration french-logo", False, "center", ("arial", "20",
             "bold"))
    t1.ct()
    t1.re(40)
    t1.ecris("Bonjour " + Tortue.monnom + " !", False, "center")
    delai(t1, 1000)
    t1.mt()
    t1.va(-200, -30)
    t1.couleur = "noir", "blanc"
    t1.debut_remplissage()
    t1.repete(2, ["av(100)", "td(90)", "av(400)", "td(90)"])
    t1.fin_remplissage()

    # Evenement 1, elementaire())
    titre = "Instructions élémentaires"
    message = "montretortue, avance, tournedroite, formes remplies, etc."
    messages(t1, titre, message)
    elementaire()
    passe()
    messages(t1, titre, message, True)
    t2.reinitialise()
    t3.reinitialise()

    # Evenement 2a, polyetcercle())
    titre = "Instruction simple, mais puissante:\npolycercle()"
    message = "Cercles, arcs de cercles et polygones."
    messages(t1, titre, message)
    polyetcerclea()
    passe()
    messages(t1, titre, message, True)
    t2.reinitialise()
    t3.reinitialise()

    # Evenement 2b, polyetcercle())
    titre = "Instruction simple, mais puissante:\npolycercle()"
    message = "Cercles, arcs de cercles et polygones."
    messages(t1, titre, message)
    polyetcercleb()
    passe()
    messages(t1, titre, message, True)
    t2.reinitialise()
    t3.reinitialise()

    # Evenement 2c, distvers())
    titre = "Distances et angles"
    message = "distance, vers."
    messages(t1, titre, message)
    distvers()
    passe()
    messages(t1, titre, message, True)
    t2.reinitialise()
    t3.reinitialise()

    # Evenement 2d, copyclown())
    titre = "Clones et tampons"
    message = str(Tortue.lis_formes()) + "\ndouble, cachet, etc."
    messages(t1, titre, message)
    copyclown()
    passe()
    messages(t1, titre, message, True)
    t2.reinitialise()
    t3.reinitialise()

    # Evenement 3a, instrepete())
    titre = "Instruction complexe"
    message = "Boucle repete(n, [\"inst1\", \"inst2\"]\nrécursive !"
    messages(t1, titre, message)
    instrepete()
    passe()
    messages(t1, titre, message, True)
    t2.reinitialise()
    t3.reinitialise()

    # Evenement 4, rosaces())
    titre = "Fractales"
    message = "Rosaces et fin de la démo ..."
    messages(t1, titre, message)
    rosaces()
    passe()
    messages(t1, titre, message, True)
    t2.reinitialise()
    t3.reinitialise()

    # Fin
    t2.ct()
    t3.ecris("Pressez entrée pour fermer le programme", False, "center",
             ("arial", "10", "bold"))
    t3.av(30)

    Tortue.lis_texte_ecran("Pour fermer ...", "... pressez entrée !")
    Tortue.au_revoir_ecran("Au revoir ...")


if __name__ == "__main__":
    demo()
