#!/usr/bin/env python
# coding=utf-8
from parapheur.parapheur import config
import os
from parapheur.parapheur import pprint


def clean(str):
    str = str.replace('\n', '')
    str = str.replace('\r', '')
    str = str.split("=", 1)
    return str[1]


def getConf():
    global conf, active, url, security_principal, credentials, groupSearchBase, personDifferentialQuery
    pprint.header("----------- Récupération des sources")
    try:
        conf = config.get("Ldapsearch", "conf_file")
    except:
        pprint.error("Fichier de conf requis: ph-init ldapsearch")

    try:
        file = open(conf, "r")
        pprint.success("OK")
    except:
        pprint.error("ERREUR : Le fichier de conf " + conf + " n'existe pas")
        exit(0)

    for line in file:
        if line.startswith("ldap.authentication.active"):
            active = clean(line)
        if line.startswith("ldap.authentication.java.naming.provider.url"):
            url = clean(line)
        if line.startswith("ldap.synchronization.java.naming.security.principal"):
            security_principal = clean(line)
        if line.startswith("ldap.synchronization.java.naming.security.credentials"):
            credentials = clean(line)
        if line.startswith("ldap.synchronization.groupSearchBase"):
            groupSearchBase = clean(line)
        if line.startswith("ldap.synchronization.personDifferentialQuery"):
            personDifferentialQuery = clean(line)
    file.close()
    return active, url, security_principal, credentials, groupSearchBase, personDifferentialQuery


def isSynchoEnable(authentication_active):
    pprint.header("----------- Synchronisation demandée ?")

    if authentication_active == "true":
        pprint.success("Synchronisation activée")
    else:
        pprint.error("ERREUR : Synchronisation désactivée")


def accessUrl(authentication_url):
    pprint.header("----------- URL accessible ?")
    url1 = authentication_url.split("//")
    url2 = url1[1].split(":")
    try:
        response = os.system("ping -c 1 " + url2[0] + " -p " + url2[1])
    except:
        response = os.system("ping -c 1 " + url2[0])

    if response == 0:
        pprint.success('Le serveur LDAP est accessible')
    else:
        pprint.error('ERREUR : Le serveur LDAP  n\'est pas accessible ' + authentication_url)


def ldapRequest(url, security_principal, credentials, groupSearchBase, personDifferentialQuery):
    global query
    pprint.header("----------- Requête LDAP")
    query = "ldapsearch -LLL -H " + url + " -x -D " + security_principal + " -w '" + credentials + "' -b '" \
            + groupSearchBase + "' '" + personDifferentialQuery + "' | grep displayName "
    pprint.info(query)
    return query


def ldapSearchGrepDisplayname():
    pprint.header("----------- Liste des utilisateurs")
    os.system(query.replace('\\', ''))


getConf()
isSynchoEnable(active)
accessUrl(url)
ldapRequest(url, security_principal, credentials, groupSearchBase, personDifferentialQuery)
ldapSearchGrepDisplayname()
