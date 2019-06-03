#!/usr/bin/env python
# coding=utf-8

import json
import time
import xml.etree.ElementTree as et
import os
from progress.bar import IncrementalBar
from progress.spinner import Spinner
import pymysql

import parapheur  # Configuration
from parapheur.parapheur import config
from parapheur.parapheur import pprint  # Colored printer

targetdir = config.get("Parapheur", "exportdir")

# Init REST API client
client = parapheur.getrestclient()

# Init database connexion
cnx = pymysql.connect(user=config.get("Database", "username"), password=config.get("Database", "password"),
                      host=config.get("Database", "server"), database=config.get("Database", "database"))

pprint.header("\nExport de la configuration du parapheur en cours ...")

if not os.path.exists(targetdir):
    os.makedirs(targetdir)
os.chdir(targetdir)


def handle_export(kind, func):
    # Handle main dir
    maindir = kind
    if not os.path.exists(maindir):
        os.makedirs(maindir)
    os.chdir(maindir)

    # Here, do stuff
    func()

    # Quit main dir
    os.chdir("..")


def user_handler():

    # Build directories structure
    os.makedirs("prefs")
    os.makedirs("sigs")
    os.makedirs("certs")
    os.makedirs("admins")

    # Get all users
    users = client.doget("/parapheur/utilisateurs")
    md4_passwords = {}

    bar = IncrementalBar('Export Utilisateurs', max=len(users), suffix='%(index)d/%(max)d - %(eta)ds')

    with open('list.json', 'w') as outfile:
        json.dump(users, outfile)

    # Get each user preferences, sig image and certificate
    for i, user in enumerate(users):
        encoded_username = user['username'].encode('utf-8')
        # Preferences
        userpref = client.doget("/api/people/%s/preferences" % encoded_username)
        with open('prefs/%s.json' % encoded_username, 'w') as outfile:
            json.dump(userpref, outfile)

        # Images
        singleuser = client.doget("/parapheur/utilisateurs/%s" % user['id'])
        if "signature" in singleuser:
            client.dodownload("/api/node/workspace/SpacesStore/%s/content" % singleuser['signature'],
                              "sigs/%s.png" % encoded_username)

        # Certificates
        if "certificat" in singleuser:
            # https://parapheur.lh.dev.libriciel.fr/iparapheur/proxy/alfresco/api/node/content%3bph%3acertificat/workspace/SpacesStore/d8a4e83b-889b-4e86-abe9-86fb5eca34f6/Delphine%20LEROUX.p12
            client.dodownload(
                "/api/node/content%%3bph%%3acertificat/workspace/SpacesStore/%s/%s" % (user['id'], encoded_username),
                "certs/%s.cer" % encoded_username)

        # Get admin fonctionnel informations
        if "admin" in singleuser and singleuser["admin"] == "adminFonctionnel":
            administres = client.doget("/parapheur/utilisateurs/%s/bureaux" % user['id'], {"administres": "true"})
            with open('admins/%s.json' % encoded_username, 'w') as outfile:
                json.dump(administres, outfile)

        cursor = cnx.cursor()
        query = "SELECT anp1.string_value " \
                "FROM alf_node_properties anp1 " \
                "INNER JOIN alf_qname aq1 " \
                "ON aq1.id = anp1.qname_id " \
                "INNER JOIN alf_node_properties anp2 " \
                "ON anp2.node_id = anp1.node_id " \
                "INNER JOIN alf_qname aq2 " \
                "ON aq2.id = anp2.qname_id " \
                "WHERE aq1.local_name    = 'password'  " \
                "AND aq2.local_name  = 'username' " \
                "AND anp2.string_value = '%s';" % (user['username'].encode('utf-8'))
        cursor.execute(query)
        for res in cursor:
            md4_passwords[user['username'].encode('utf-8')] = res[0]

        bar.next()

    with open('passwords.json', 'w') as outfile:
        json.dump(md4_passwords, outfile)

    bar.finish()
    time.sleep(0.1)


def groups_handler():

    # Get all groups
    groups = client.doget("/parapheur/groupes")

    bar = IncrementalBar('Export Groupes     ', max=len(groups), suffix='%(index)d/%(max)d - %(eta)ds')

    with open('list.json', 'w') as outfile:
        json.dump(groups, outfile)

    # Get detail for each group
    for i, group in enumerate(groups):
        detail_group = client.doget("/parapheur/groupes/%s" % group["id"])
        with open('%s.json' % group["id"], 'w') as outfile:
            json.dump(detail_group, outfile)

        bar.next()

    bar.finish()
    time.sleep(0.1)


def bureaux_handler():

    # Get all bureaux
    bureaux = client.doget("/parapheur/bureaux", {"asAdmin": "true"})

    bar = IncrementalBar('Export Bureaux     ', max=len(bureaux), suffix='%(index)d/%(max)d - %(eta)ds')

    for i, bureau in enumerate(bureaux):
        response = client.doget("/parapheur/bureaux/%s/associes" % bureau['id'], {"asAdmin": "true"})
        if 'delegations-possibles' in response:
            bureau['delegations-possibles'] = response['delegations-possibles']
            bureaux[i] = bureau

        bar.next()

    with open('list.json', 'w') as outfile:
        json.dump(bureaux, outfile)

    bar.finish()
    time.sleep(0.1)


def circuits_handler():

    spinner = Spinner('Export Circuits ...')

    spinner.next()
    # Get all circuits
    circuits = client.doget("/parapheur/circuits")

    with open('list.json', 'w') as outfile:
        json.dump(circuits, outfile)


def types_handler():

    # Get all types
    types = client.doget("/parapheur/types", {"asAdmin": "true"})

    with open('list.json', 'w') as outfile:
        json.dump(types, outfile)

    bar = IncrementalBar('Export Types       ', max=len(types), suffix='%(index)d/%(max)d - %(eta)ds')

    # For each type, get all subtypes
    for i, typo in enumerate(types):
        # There is PAdES configuration... We need to get it back !
        if 'PAdES' in typo['sigFormat']:
            pades_config = client.doget("/parapheur/types/%s/overridePades" % typo["id"].encode('utf-8'))
            with open('%s_pades.json' % typo["id"].encode('utf-8'), 'w') as outfile:
                json.dump(pades_config, outfile)
        if 'ACTES' in typo['tdtProtocole']:
            actes_config = client.doget("/parapheur/types/%s/overrideActes" % typo["id"].encode('utf-8'))
            with open('%s_actes.json' % typo["id"].encode('utf-8'), 'w') as outfile:
                json.dump(actes_config, outfile)
        if 'HELIOS' in typo['tdtProtocole']:
            helios_config = client.doget("/parapheur/types/%s/overrideHelios" % typo["id"].encode('utf-8'))
            with open('%s_helios.json' % typo["id"].encode('utf-8'), 'w') as outfile:
                json.dump(helios_config, outfile)
        # Create path for typo
        os.makedirs(typo["id"])
        os.chdir(typo["id"])
        for subtype in typo["sousTypes"]:
            subtype_info = client.doget(
                "/parapheur/types/%s/%s" % (subtype["parent"].encode('utf-8'), subtype["id"].encode('utf-8')))
            with open('%s.json' % subtype["id"].encode('utf-8'), 'w') as outfile:
                json.dump(subtype_info, outfile)
        os.chdir("..")

        bar.next()

    bar.finish()
    time.sleep(0.1)


def metadata_hanlder():

    spinner = Spinner('Export Metadonnees ...')

    spinner.next()

    metadatas = client.doget("/parapheur/metadonnees", {"asAdmin": "true"})

    with open('list.json', 'w') as outfile:
        json.dump(metadatas, outfile)


def calque_handler():

    calques = client.doget("/parapheur/calques")

    with open('list.json', 'w') as outfile:
        json.dump(calques, outfile)

    bar = IncrementalBar('Export Calques     ', max=len(calques), suffix='%(index)d/%(max)d - %(eta)ds')

    for i, calque in enumerate(calques):
        calque_encoded = calque['id']
        if not os.path.exists(calque_encoded):
            os.mkdir(calque_encoded)
            os.chdir(calque_encoded)

            # do stuffs like getting all infos
            signature = client.doget("/parapheur/calques/%s/signature" % calque['id'])
            with open('signature.json', 'w') as outfile:
                json.dump(signature, outfile)

            images = client.doget("/parapheur/calques/%s/image" % calque['id'])
            with open('image.json', 'w') as outfile:
                json.dump(images, outfile)
            # for each image get the actual file in base
            for image in images:
                imagename = image['nomImage'].encode('utf-8')
                client.dodownloadfromnode("/workspace/SpacesStore/%s/file.bin" % image['id'],
                                          "{http://www.starxpert.fr/alfresco/model/calque/1.0}contenuImage",
                                          "%s" % imagename)

            commentaire = client.doget("/parapheur/calques/%s/commentaire" % calque['id'])
            with open('commentaire.json', 'w') as outfile:
                json.dump(commentaire, outfile)
            metadata = client.doget("/parapheur/calques/%s/metadata" % calque['id'])
            with open('metadata.json', 'w') as outfile:
                json.dump(metadata, outfile)

            os.chdir('..')

        bar.next()

    bar.finish()
    time.sleep(0.1)


def advanced_handler():

    spinner = Spinner('Export Conf. avancee ...')

    os.mkdir("certs")

    # https://parapheur.test.adullact.org/iparapheur/proxy/alfresco/slingshot/doclib/treenode/node/alfresco/company/home/Dictionnaire%20de%20donn%C3%A9es/Certificats
    # Get certificates noderef
    response = client.doget(
        '/slingshot/doclib/treenode/node/alfresco/company/home/Dictionnaire%20de%20données/Certificats')

    spinner.next()

    certs_id = response["parent"]["nodeRef"].split('/')[-1]
    response = client.doget("/cmis/s/workspace:SpacesStore/i/%s/children" % certs_id)

    spinner.next()

    # Parse the XML result
    root_tag = et.ElementTree(et.fromstring(response)).getroot()
    for child in root_tag.iter("{http://www.w3.org/2005/Atom}entry"):
        content_url = child.find("{http://www.w3.org/2005/Atom}content").get('src').split('alfresco/wcs')[1]
        content_title = child.find("{http://www.w3.org/2005/Atom}title").text

        if content_url.endswith('.p12'):
            client.dodownload(content_url, "certs/%s" % content_title.encode('utf-8'))
            spinner.next()

    actes_infos = client.doget("/parapheur/connecteurs/s2low/actes")
    with open('actes.json', 'w') as outfile:
        json.dump(actes_infos, outfile)

    spinner.next()

    helios_infos = client.doget("/parapheur/connecteurs/s2low/helios")
    with open('helios.json', 'w') as outfile:
        json.dump(helios_infos, outfile)

    spinner.next()

    mailsec_infos = client.doget("/parapheur/connecteurs/s2low/mailsec")
    with open('mailsec.json', 'w') as outfile:
        json.dump(mailsec_infos, outfile)

    spinner.next()


handle_export("users", user_handler)
handle_export("groups", groups_handler)
handle_export("bureaux", bureaux_handler)
handle_export("circuits", circuits_handler)
handle_export("types", types_handler)
handle_export("metadatas", metadata_hanlder)
handle_export("calques", calque_handler)
handle_export("advanced", advanced_handler)
