# coding=utf-8

import parapheur
from progress.bar import IncrementalBar

client = parapheur.getrestclient()

if client.islogged:
    utilisateurs = client.doget("/parapheur/utilisateurs")
    bar = IncrementalBar('Analyse des utilisateurs', max=len(utilisateurs), suffix='%(index)d/%(max)d - %(eta)ds')

    to_delete = []

    for user in utilisateurs:
        if user["isFromLdap"]:
            bureaux = client.doget("/parapheur/utilisateurs/%s/bureaux" % user["id"], {"administres": "false"})
            if len(bureaux) == 0:
                to_delete.append(user)
                client.dodelete("/parapheur/utilisateurs/%s" % user["id"])

        bar.next()

    bar.finish()

    bar = IncrementalBar('Suppression des utilisateurs LDAP inutiles', max=len(to_delete), suffix='%(index)d/%(max)d - %(eta)ds')

    for user in to_delete:
        client.dodelete("/parapheur/utilisateurs/%s" % user["id"])
        bar.next()

    bar.finish()