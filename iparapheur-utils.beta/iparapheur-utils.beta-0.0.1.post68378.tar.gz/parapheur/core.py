#!/usr/bin/env python
# coding=utf-8

# Parapheur API
import parapheur
# Scripts API
import scripts
# arguments
import gettext

__author__ = 'Lukas Hameury'

__all__ = ['init', 'echo', 'check']


def convertmessages(s):
    subdict = \
        {'positional arguments': 'Arguments',
         'optional arguments': 'Arguments',
         'show this help message and exit': 'Affiche ce message et quitte'}
    if s in subdict:
        s = subdict[s]
    return s


gettext.gettext = convertmessages
import argparse


def init():
    parser = argparse.ArgumentParser(
        prog='ph-init',
        description="Génère un fichier de configuration par défaut dans le répertoire courant")
    parser.add_argument('-p', help='Chemin du fichier de configuration')
    parser.add_argument('-c', help='Commande pour laquelle générer le fichier de configuration',
                        choices=["recuparchives", "export", "import", "pushdoc", "ipclean", "ldapsearch",
                                 "reset_admin_password"])

    args = parser.parse_args()

    filename = "script"
    path = "."
    if args.p:
        path = args.p
    if args.c:
        filename = args.c

    # Copy the configuration file
    parapheur.copyconfig(filename, path)

    print("Fichier de configuration 'iparapheur-utils.cfg' créé")


def echo():
    parser = argparse.ArgumentParser(
        prog='ph-echo',
        description="Lance un echo via webservice sur un iParapheur")

    parser.add_argument('-s', help="URL du serveur iParapheur")
    parser.add_argument('-c', help='Fichier de configuration')
    parser.add_argument('-u', help='Utilisateur')
    parser.add_argument('-p', help='Mot de passe')

    args = parser.parse_args()

    if args.c:
        parapheur.setconfig(args.c)
    if args.s:
        parapheur.setconfigproperty("Parapheur", "server", args.s)
    if args.u:
        parapheur.setconfigproperty("Parapheur", "username", args.u)
    if args.p:
        parapheur.setconfigproperty("Parapheur", "password", args.p)

    # Initialisation d'API SOAP
    webservice = parapheur.getsoapclient()
    print(webservice.call().echo("coucou"))


def check():
    scripts.checkinstallation()


def recuparchives():
    parser = argparse.ArgumentParser(
        prog='ph-recupArchives',
        description="Lance une récupération / purge des archives")

    parser.add_argument('-s', help="URL du serveur iParapheur")
    parser.add_argument('-c', help='Fichier de configuration')
    parser.add_argument('-u', help='Utilisateur')
    parser.add_argument('-p', help='Mot de passe')

    parser.add_argument('-f', help='Répertoire de destination')
    parser.add_argument('-ps', help='Taille des pages à récupérer')
    parser.add_argument('-r', help='Chemins réduis des téléchargements', choices=["true", "false"])
    parser.add_argument('-pu', help='Active la purge les données', choices=["true", "false"])
    parser.add_argument('-d', help='Télécharge les données', choices=["true", "false"])
    parser.add_argument('-pdf', help='Télécharge seulement les bordereaux PDF', choices=["true", "false"])
    parser.add_argument('-t', help='Filtre sur type')
    parser.add_argument('-st', help='Filtre sur sous-type')
    parser.add_argument('-w', help='Délai de conservation des données')

    args = parser.parse_args()

    if args.c:
        parapheur.setconfig(args.c)
    if args.s:
        parapheur.setconfigproperty("Parapheur", "server", args.s)
    if args.u:
        parapheur.setconfigproperty("Parapheur", "username", args.u)
    if args.p:
        parapheur.setconfigproperty("Parapheur", "password", args.p)

    if args.f:
        parapheur.setconfigproperty("RecupArchives", "folder", args.f)
    if args.ps:
        parapheur.setconfigproperty("RecupArchives", "page_size", args.ps)
    if args.r:
        parapheur.setconfigproperty("RecupArchives", "use_reduced_download_path", args.r)
    if args.pdf:
        parapheur.setconfigproperty("RecupArchives", "use_only_print_pdfs", args.pdf)
    if args.pu:
        parapheur.setconfigproperty("RecupArchives", "purge", args.pu)
    if args.d:
        parapheur.setconfigproperty("RecupArchives", "download", args.d)
    if args.t:
        parapheur.setconfigproperty("RecupArchives", "type_filter", args.t)
    if args.st:
        parapheur.setconfigproperty("RecupArchives", "subtype_filter", args.st)
    if args.w:
        parapheur.setconfigproperty("RecupArchives", "waiting_days", args.w)

    # Lancement du script
    scripts.recuparchives()


def import_data():
    parser = argparse.ArgumentParser(
        prog='ph-import',
        description="Importe la configuration ciblée dans un parapheur vierge")

    parser.add_argument('-s', help="URL du serveur iParapheur")
    parser.add_argument('-c', help='Fichier de configuration')
    parser.add_argument('-u', help='Utilisateur administrateur')
    parser.add_argument('-p', help='Mot de passe')
    parser.add_argument('-i', help='Répertoire à importer')

    parser.add_argument('-dh', help='IP du serveur mysql')
    parser.add_argument('-dp', help='Port du serveur mysql')
    parser.add_argument('-du', help='Utilisateur alfresco de mysql')
    parser.add_argument('-dpw', help='Mot de passe utilisateur alfresco de mysql')
    parser.add_argument('-dd', help='Nom de la base mysql')

    args = parser.parse_args()

    if args.c:
        parapheur.setconfig(args.c)
    if args.s:
        parapheur.setconfigproperty("Parapheur", "server", args.s)
    if args.u:
        parapheur.setconfigproperty("Parapheur", "username", args.u)
    if args.p:
        parapheur.setconfigproperty("Parapheur", "password", args.p)
    if args.i:
        parapheur.setconfigproperty("Parapheur", "importdir", args.i)

    if args.dh:
        parapheur.setconfigproperty("Database", "server", args.dh)
    if args.dp:
        parapheur.setconfigproperty("Database", "port", args.dp)
    if args.du:
        parapheur.setconfigproperty("Database", "username", args.du)
    if args.dpw:
        parapheur.setconfigproperty("Database", "password", args.dpw)
    if args.dd:
        parapheur.setconfigproperty("Database", "database", args.dd)

    # Lancement de l'import
    scripts.import_data()


def export_data():
    parser = argparse.ArgumentParser(
        prog='ph-export',
        description="Exporte la configuration du parapheur ciblé vers un dossier")

    parser.add_argument('-s', help="URL du serveur iParapheur")
    parser.add_argument('-c', help='Fichier de configuration')
    parser.add_argument('-u', help='Utilisateur administrateur')
    parser.add_argument('-p', help='Mot de passe')
    parser.add_argument('-i', help='Répertoire de destination')

    parser.add_argument('-dh', help='IP du serveur mysql')
    parser.add_argument('-dp', help='Port du serveur mysql')
    parser.add_argument('-du', help='Utilisateur alfresco de mysql')
    parser.add_argument('-dpw', help='Mot de passe utilisateur alfresco de mysql')
    parser.add_argument('-dd', help='Nom de la base mysql')

    parser.add_argument('-ou', help='Importer les users')
    parser.add_argument('-og', help='Importer les groupes')
    parser.add_argument('-ob', help='Importer les bureaux')
    parser.add_argument('-oc', help='Importer les circuits')
    parser.add_argument('-ot', help='Importer les types et sous-types')
    parser.add_argument('-om', help='Importer les metadatas')
    parser.add_argument('-oq', help='Importer les calques')
    parser.add_argument('-oa', help='Importer les advanced')

    args = parser.parse_args()

    if args.c:
        parapheur.setconfig(args.c)
    if args.s:
        parapheur.setconfigproperty("Parapheur", "server", args.s)
    if args.u:
        parapheur.setconfigproperty("Parapheur", "username", args.u)
    if args.p:
        parapheur.setconfigproperty("Parapheur", "password", args.p)
    if args.i:
        parapheur.setconfigproperty("Parapheur", "exportdir", args.i)

    if args.dh:
        parapheur.setconfigproperty("Database", "server", args.dh)
    if args.dp:
        parapheur.setconfigproperty("Database", "port", args.dp)
    if args.du:
        parapheur.setconfigproperty("Database", "username", args.du)
    if args.dpw:
        parapheur.setconfigproperty("Database", "password", args.dpw)
    if args.dd:
        parapheur.setconfigproperty("Database", "database", args.dd)

    if args.ou:
        parapheur.setconfigproperty("Object", "users", args.ou)
    if args.og:
        parapheur.setconfigproperty("Object", "groupes", args.og)
    if args.ob:
        parapheur.setconfigproperty("Object", "bureaux", args.ob)
    if args.oc:
        parapheur.setconfigproperty("Object", "circuits", args.oc)
    if args.ot:
        parapheur.setconfigproperty("Object", "types_soustypes", args.ot)
    if args.om:
        parapheur.setconfigproperty("Object", "metadatas", args.om)
    if args.oq:
        parapheur.setconfigproperty("Object", "calques", args.oq)
    if args.oa:
        parapheur.setconfigproperty("Object", "advanced", args.oa)

    # Lancement de l'import
    scripts.export_data()


def rename():
    parser = argparse.ArgumentParser(
        prog='ph-rename',
        description="Change l'URL d'accès du i-Parapheur")

    parser.add_argument('-n', help="Nouvelle URL du serveur iParapheur", required=True)

    args = parser.parse_args()

    parapheur.setconfigproperty("Parapheur", "new_url", args.n)

    # Lancement du changement de nom
    scripts.rename()


def remove_ldap():
    parser = argparse.ArgumentParser(
        prog='ph-removeldap',
        description="Supprime les utilisateurs synchronisés LDAP n'ayant aucune liaison avec un bureau")

    args = parser.parse_args()

    # Lancement du changement de nom
    scripts.remove_ldap()


def pushdoc():
    parser = argparse.ArgumentParser(
        prog='ph-pushdoc',
        description="Permet une gestion plus simple du connecteur générique pushdoc dans les cas les plus classiques")

    parser.add_argument('-c', help='Fichier de configuration')

    parser.add_argument('-j', help='Fichier JAR du pushdoc')
    parser.add_argument('-i', help='Répertoire à traiter')
    parser.add_argument('-e', help='Courriel de l\'utilisateur webservice')
    parser.add_argument('-x', help='xPath par défaut dans le cas d\'un envoi de flux PES')
    parser.add_argument('-v', help='Visuel PDF à utiliser dans le cas d\'un envoi de flux PES')

    args = parser.parse_args()

    if args.c:
        parapheur.setconfig(args.c)
    if args.j:
        parapheur.setconfigproperty("Pushdoc", "jar_file", args.j)
    if args.i:
        parapheur.setconfigproperty("Pushdoc", "import_dir", args.i)
    if args.e:
        parapheur.setconfigproperty("Pushdoc", "user_mail", args.e)
    if args.x:
        parapheur.setconfigproperty("Pushdoc", "default_xpath", args.x)
    if args.v:
        parapheur.setconfigproperty("Pushdoc", "template_pdf_file", args.v)

    # Lancement du pushdoc
    scripts.pushdoc()


def ipclean():
    parser = argparse.ArgumentParser(
        prog='ph-ipclean',
        description="Génère les index avec redémarrage de l'application")

    # Lancement du changement de nom
    scripts.ipclean()


def ldapsearch():
    parser = argparse.ArgumentParser(
        prog='ph-ldapsearch',
        description="Vérifie la configuration du LDAP et affiche les utilisateurs retournés par la requête")

    parser.add_argument('-j', help='Fichier conf')
    args = parser.parse_args()

    if args.j:
        parapheur.setconfigproperty("Ldapsearch", "conf_file", args.j)

    # Lancement du ldapsearch
    scripts.ldapsearch()


def count_files():
    parser = argparse.ArgumentParser(
        prog='ph-count_files',
        description="Affiche un tableau des dossiers par bureaux")

    # Lancement du changement de nom
    scripts.count_files()


def reset_admin_password():
    parser = argparse.ArgumentParser(
        prog='ph-reset_admin_password',
        description="Réinitialise le mot de passe de l'admin")

    parser.add_argument('-c', help='Fichier de configuration')
    parser.add_argument('-dh', help='IP du serveur mysql')
    parser.add_argument('-dp', help='Port du serveur mysql')
    parser.add_argument('-du', help='Utilisateur alfresco de mysql')
    parser.add_argument('-dpw', help='Mot de passe utilisateur alfresco de mysql')
    parser.add_argument('-dd', help='Nom de la base mysql')

    args = parser.parse_args()

    if args.c:
        parapheur.setconfig(args.c)

    if args.dh:
        parapheur.setconfigproperty("Database", "server", args.dh)
    if args.dp:
        parapheur.setconfigproperty("Database", "port", args.dp)
    if args.du:
        parapheur.setconfigproperty("Database", "username", args.du)
    if args.dpw:
        parapheur.setconfigproperty("Database", "password", args.dpw)
    if args.dd:
        parapheur.setconfigproperty("Database", "database", args.dd)

    # Réinitionlisation du mot de passe admin
    scripts.reset_admin_password()


def properties_merger():
    scripts.properties_merger()


if __name__ == "__main__":
    properties_merger()
