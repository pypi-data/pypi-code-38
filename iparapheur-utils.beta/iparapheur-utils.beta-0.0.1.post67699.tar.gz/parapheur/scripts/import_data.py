#!/usr/bin/env python
# coding=utf-8

import copy
import json
import time

import os
import pymysql
from parapheur.parapheur import config
from progress.bar import IncrementalBar

import parapheur  # Configuration

importdir = config.get("Parapheur", "importdir")
os.chdir(importdir)

# Init REST API client
client = parapheur.getrestclient()

# Init database connexion
cnx = pymysql.connect(user=config.get("Database", "username"), password=config.get("Database", "password"),
                      host=config.get("Database", "server"), database=config.get("Database", "database"))


class ParapheurImportTemplate(object):
    """
    This is the template for importing data in parapheur
    """

    def __init__(self, _importdir, _name, _client):
        self.importdir = _importdir
        self.client = _client
        self.name = _name
        self.launch()

    def __before_func__(self):
        print("This have to be implemented - Return list of elements")
        return []

    def __each_func__(self, element):
        print("This have to be implemented - Return updated element")
        return element

    def __after_func__(self):
        print("This have to be implemented")

    def launch(self):
        """
        This method is just a template for importing things properly ...
        :return: nothing, it just logs a progressbar
        """

        list_to_handle = self.__before_func__()

        bar = IncrementalBar('Importing %s ...' % self.name.encode('utf-8'), max=len(list_to_handle),
                             suffix='%(index)d/%(max)d - %(eta)ds')

        for i, element in enumerate(list_to_handle):
            list_to_handle[i] = self.__each_func__(element)
            bar.next()

        self.__after_func__()
        bar.finish()
        time.sleep(0.1)


class UsersImport(ParapheurImportTemplate):
    def __before_func__(self):
        self.users = None
        with open("users/list.json") as data_file:
            self.users = json.load(data_file)
        # Load passwords
        self.passwords = {}
        with open("users/passwords.json") as data_file:
            self.passwords = json.load(data_file)
        # Get all users
        self.users_exists = client.doget("/parapheur/utilisateurs")
        return self.users

    def __each_func__(self, element):
        encoded_username = element['username'].encode('utf-8')
        # 1 - Create users
        element['password'] = "secret1"
        if "firstName" not in element:
            element["firstName"] = ""
        if "lastName" not in element:
            element["lastName"] = ""
        if "email" not in element:
            element["email"] = ""
        response = client.dopost("/parapheur/utilisateurs", element)
        # Si l'utilisateur n'existe pas, on le crée
        if response['id'] != "already exists":
            element['id'] = response['id']
        # Sinon, on récupère l'id existant
        else:
            user_exists = (x for x in self.users_exists if x['username'] == element['username']).next()
            element['id'] = user_exists['id']

        # 2 - Update all properties + sigs + cert
        if os.path.isfile("users/sigs/%s.png" % encoded_username):
            # We have a sig image !
            element['signatureData'] = client.load_binary_file("users/sigs/%s.png" % encoded_username)
        if os.path.isfile("users/certs/%s.cer" % encoded_username):
            # We have a certificate !
            element['certificat'] = {
                "content": client.load_binary_file("users/certs/%s.cer" % encoded_username)
            }

        client.doput("/parapheur/utilisateurs/%s" % element['id'], element)

        # Import preferences
        with open("users/prefs/%s.json" % encoded_username) as data_file:
            prefs = json.load(data_file)
            client.dodelete("/api/people/%s/preferences" % encoded_username)
            client.dopost("/api/people/%s/preferences" % encoded_username, prefs)

        # In some cases, user does not have a password
        if encoded_username in self.passwords:
            # We have to get node_id and qname_id of user before updating password...
            cursor = cnx.cursor()
            query = "SELECT anp1.node_id, anp1.qname_id " \
                    "FROM alf_node_properties anp1 " \
                    "INNER JOIN alf_qname aq1 " \
                    "ON aq1.id = anp1.qname_id " \
                    "INNER JOIN alf_node_properties anp2 " \
                    "ON anp2.node_id = anp1.node_id " \
                    "INNER JOIN alf_qname aq2 " \
                    "ON aq2.id = anp2.qname_id " \
                    "WHERE aq1.local_name    = 'password'  " \
                    "AND aq2.local_name  = 'username' " \
                    "AND anp2.string_value = '%s';" % encoded_username
            cursor.execute(query)
            for res in cursor:
                cursor = cnx.cursor()
                # We only have one result !
                updating_passord_query = "UPDATE alf_node_properties " \
                                         "SET string_value='%s' " \
                                         "WHERE node_id=%s " \
                                         "AND qname_id=%s;" % (self.passwords[encoded_username], res[0], res[1])
                cursor.execute(updating_passord_query)
                # Actually commit the transaction
                cnx.commit()
        return element

    def __after_func__(self):
        pass


class GroupsImport(ParapheurImportTemplate):
    def __before_func__(self):
        self.groups = None

        with open("groups/list.json") as data_file:
            self.groups = json.load(data_file)

        # Get all groups
        self.groups_exists = client.doget("/parapheur/groupes")
        # Keep the old ones for id references
        self.old_groups = copy.deepcopy(self.groups)

        return self.groups

    def __each_func__(self, element):
        # complete group
        with open("groups/%s.json" % element['id']) as data_file:
            groups_detail = json.load(data_file)
            element.update(groups_detail)
        response = client.dopost("/parapheur/groupes", element)
        if not response:
            print('error during request')
        else:
            if "status" not in response:
                # group created
                element['id'] = response['id']
            else:
                # group exist
                group_exists = (x for x in self.groups_exists if x['shortName'] == element['shortName']).next()
                element['id'] = group_exists['id']
        for member in element['users']:
            # Add each member to group
            client.dopost("/parapheur/groupes/%s/%s" % (element['id'], member['shortName'].encode('utf-8')))
        return element

    def __after_func__(self):
        # We have to build dict with old and new groups ids
        self.group_ids_relation = {}
        for group in self.groups:
            old_b = (b for b in self.old_groups if b['shortName'] == group['shortName']).next()
            self.group_ids_relation[old_b['id']] = group['id']


class MetasImport(ParapheurImportTemplate):
    def __before_func__(self):
        with open("metadatas/list.json") as data_file:
            metadatas = json.load(data_file)
        return metadatas

    def __each_func__(self, element):
        client.dopost("/parapheur/metadonnees/%s" % element['id'], element)
        return element

    def __after_func__(self):
        pass


class BureauxImport(ParapheurImportTemplate):
    def __before_func__(self):
        self.bureaux = None
        with open("bureaux/list.json") as data_file:
            self.bureaux = json.load(data_file)

        # Get all bureaux
        self.bureaux_exists = client.doget("/parapheur/bureaux", {"asAdmin": "true"})
        # Keep the old ones for id references
        self.old_bureaux = copy.deepcopy(self.bureaux)
        return self.bureaux

    def __each_func__(self, element):
        # Ugly hack for bureaux random errors
        while True:
            if not any(x['name'] == element['name'] for x in self.bureaux_exists):
                # We have to remove "null" habilitations
                for k, v in element.items():
                    if v is None:
                        del element[k]
                try:
                    response = client.dopost("/parapheur/bureaux", element)
                    element['id'] = response['id']
                    break
                except:
                    # Refresh local bureaux
                    self.bureaux_exists = client.doget("/parapheur/bureaux", {"asAdmin": "true"})
            else:
                bureau_exists = (x for x in self.bureaux_exists if x['name'] == element['name']).next()
                element['id'] = bureau_exists['id']
                break
        return element

    def __after_func__(self):
        # We have to build dict with old and new bureaux ids
        self.bureau_ids_relation = {}
        for bureau in self.bureaux:
            old_b = (b for b in self.old_bureaux if b['name'] == bureau['name']).next()
            self.bureau_ids_relation[old_b['id']] = bureau['id']


class BureauxAdvancedImport(ParapheurImportTemplate):
    def __init__(self, _importdir, _client, _users, _bureaux, _bureau_ids_relation):
        self.bureaux = _bureaux
        self.users = _users
        self.bureau_ids_relation = _bureau_ids_relation
        super(BureauxAdvancedImport, self).__init__(_importdir, "advanced bureaux configuration", _client)

    def __before_func__(self):
        return self.bureaux

    def __each_func__(self, element):
        element['delegations-possibles'] = [self.bureau_ids_relation[x] for x in element['delegations-possibles']]
        to_update = {'delegations-possibles': element['delegations-possibles']}

        if element["hierarchie"]:
            element['hierarchie'] = self.bureau_ids_relation[element['hierarchie']]
            to_update['hierarchie'] = element['hierarchie']

        client.doput("/parapheur/bureaux/%s" % element['id'], to_update)

        if "idCible" in element["delegation"]:
            element['delegation']["idCible"] = self.bureau_ids_relation[element['delegation']["idCible"]]
            client.doput("/parapheur/delegations/%s" % element['id'], element['delegation'])

        return element

    def __after_func__(self):
        for i, user in enumerate(self.users):
            if os.path.isfile("users/admins/%s.json" % user['username'].encode('utf-8')):
                with open("users/admins/%s.json" % user['username'].encode('utf-8'), "r") as json_file:
                    # Remove duplicates
                    administres = list(set(json.load(json_file)))
                    # Correct ids of bureaux
                    administres = [self.bureau_ids_relation[x] for x in administres]
                    client.doput("/parapheur/utilisateurs/%s" % user['id'], {
                        "admin": "adminFonctionnel",
                        "bureauxAdministres": administres,
                        "isAdmin": False,
                        "isAdminFonctionnel": True
                    })


class CircuitsImport(ParapheurImportTemplate):
    def __init__(self, _importdir, _client, _bureau_ids_relation):
        self.bureau_ids_relation = _bureau_ids_relation
        super(CircuitsImport, self).__init__(_importdir, "circuits", _client)

    def __before_func__(self):
        with open("circuits/list.json") as data_file:
            circuits = json.load(data_file)

        # Get all users
        self.circuits_exists = client.doget("/parapheur/circuits")

        return circuits

    def __each_func__(self, element):
        # Replace all occurence of bureau id in each step
        for j, step in enumerate(element['etapes']):
            if "parapheur" in step:
                step['parapheur'] = self.bureau_ids_relation[step['parapheur']]
                step['listeNotification'] = [self.bureau_ids_relation[x] if x != "_emetteur_" else "_emetteur_" for x in
                                             step['listeNotification']]
            element['etapes'][j] = step

        client.dopost("/parapheur/circuits", element)

        return element

    def __after_func__(self):
        pass


class TyposImports(ParapheurImportTemplate):
    def __init__(self, _importdir, _client, _bureau_ids_relation, _group_ids_relation, _calque_ids_relation):
        self.bureau_ids_relation = _bureau_ids_relation
        self.group_ids_relation = _group_ids_relation
        self.calque_ids_relation = _calque_ids_relation

        super(TyposImports, self).__init__(_importdir, "typologies", _client)

    def __before_func__(self):
        with open("types/list.json") as data_file:
            types = json.load(data_file)
        return types

    def __each_func__(self, element):
        # Create type
        client.dopost("/parapheur/types/%s" % element['id'].encode('utf-8'), element)

        # Eventually do pades thing
        if os.path.isfile("types/%s_pades.json" % element['id'].encode('utf-8')):
            with open("types/%s_pades.json" % element['id'].encode("utf-8")) as data_file:
                pades_info = json.load(data_file)
                client.doput("/parapheur/types/%s/overridePades" % element['id'].encode("utf-8"),
                             pades_info['overridedTdt'])
        # Eventually do actes thing
        if os.path.isfile("types/%s_actes.json" % element['id'].encode('utf-8')):
            with open("types/%s_actes.json" % element['id'].encode("utf-8")) as data_file:
                actes_info = json.load(data_file)['overridedTdt']
                if os.path.isfile("advanced/certs/%s" % actes_info['name'].encode('utf-8')):
                    base64cert = client.load_binary_file("advanced/certs/%s" % actes_info['name'].encode('utf-8'))
                    actes_info['cert'] = base64cert
                    client.doput("/parapheur/types/%s/overrideActes" % element['id'].encode("utf-8"),
                                 actes_info)
        # Eventually do helios thing
        if os.path.isfile("types/%s_helios.json" % element['id'].encode('utf-8')):
            with open("types/%s_helios.json" % element['id'].encode("utf-8")) as data_file:
                helios_info = json.load(data_file)['overridedTdt']
                if os.path.isfile("advanced/certs/%s" % helios_info['name'].encode('utf-8')):
                    base64cert = client.load_binary_file("advanced/certs/%s" % helios_info['name'].encode('utf-8'))
                    helios_info['cert'] = base64cert
                    client.doput("/parapheur/types/%s/overrideHelios" % element['id'].encode("utf-8"),
                                 helios_info)

        # Create all subtypes
        for subtype in element['sousTypes']:
            with open("types/%s/%s.json" % (element['id'].encode("utf-8"), subtype['id'].encode("utf-8"))) as data_file:
                subtype_info = json.load(data_file)
            # Correct ids for bureaux
            subtype_info['parapheurs'] = [self.bureau_ids_relation[x] for x in subtype_info['parapheurs']]
            subtype_info['parapheursFilters'] = [self.bureau_ids_relation[x] for x in subtype_info['parapheursFilters']]
            # Correct ids for groups
            try:
                subtype_info['groups'] = [self.group_ids_relation[x] if x in self.group_ids_relation else x for x in
                                          subtype_info['groups']]
            except:
                # ignore
                print("Error : cannot find group")
            try:
                subtype_info['groupsFilters'] = [self.group_ids_relation[x] if x in self.group_ids_relation else x for x
                                                 in subtype_info['groupsFilters']]
            except:
                # ignore
                print("Error : cannot find group")
            # Correct ids for calques
            for j, calque in enumerate(subtype_info['calques']):
                calque['id'] = self.calque_ids_relation[calque['id']]
                subtype_info['calques'][j] = calque

            # Create subtype
            client.dopost(
                "/parapheur/types/%s/%s" % (element['id'].encode("utf-8"), subtype['id'].encode("utf-8")), subtype_info)
        return element

    def __after_func__(self):
        pass


class CalquesImport(ParapheurImportTemplate):
    def __before_func__(self):
        with open("calques/list.json") as data_file:
            self.calques = json.load(data_file)

        # Get all users
        self.circuits_exists = client.doget("/parapheur/circuits")
        self.calque_ids_relation = {}

        return self.calques

    def __each_func__(self, element):
        # Create the calque
        response = client.dopost("/parapheur/calques", element)

        old_id = element['id']
        self.calque_ids_relation[element['id']] = response['id']
        element['id'] = response['id']

        def loadmetaobj(name, police_number=False):
            # Then create all subelements
            with open("calques/%s/%s.json" % (old_id, name)) as data_file:
                elements = json.load(data_file)
                for com in elements:
                    if com['postSignature'] is None:
                        com['postSignature'] = False
                    for k, v in com.items():
                        if isinstance(v, int) and not isinstance(v, bool):
                            com[k] = str(v)
                    if police_number:
                        com['taillePolice'] = int(com['taillePolice'])
                    if "nomImage" in com:
                        binary_img = client.load_binary_file(
                            "calques/%s/%s" % (old_id, com['nomImage'].encode('utf-8')))
                        com['fichierImage'] = binary_img
                    client.dopost("/parapheur/calques/%s/%s" % (element['id'], name), com)

        loadmetaobj("commentaire")
        loadmetaobj("metadata", True)
        loadmetaobj("signature")
        loadmetaobj("image")

        return element

    def __after_func__(self):
        pass


class AdvancedImport(ParapheurImportTemplate):
    def __before_func__(self):
        return ['actes', 'helios', 'mailsec']

    def __each_func__(self, element):
        with open("advanced/%s.json" % element) as data_file:
            data = json.load(data_file)
            # Load cert file if exist
            if os.path.isfile("advanced/certs/%s" % data['name'].encode('utf-8')):
                base64cert = client.load_binary_file("advanced/certs/%s" % data['name'].encode('utf-8'))
                data['cert'] = base64cert
                client.doput("/parapheur/connecteurs/s2low/%s" % element, data)

        return element

    def __after_func__(self):
        pass


# Classic user import
importedUsers = UsersImport(importdir, "users", client)
# Groups import, keep saved groups for ids relationship
importedGroups = GroupsImport(importdir, "groups", client)
# Classic metas import
MetasImport(importdir, "metadatas", client)
# Classic calques import
importedCalques = CalquesImport(importdir, "calques", client)
# Bureaux import, keep saved ones for ids relationship
importedBureaux = BureauxImport(importdir, "bureaux", client)
# Advanced configuration import with previously saved infos
BureauxAdvancedImport(importdir, client, importedUsers.users, importedBureaux.bureaux,
                      importedBureaux.bureau_ids_relation)
# Circuits import with previously saved infos
CircuitsImport(importdir, client, importedBureaux.bureau_ids_relation)
# Typo import with bureaux and groups ids relationship
TyposImports(importdir, client, importedBureaux.bureau_ids_relation, importedGroups.group_ids_relation,
             importedCalques.calque_ids_relation)
# Import Actes, Helios and mailsec configuration
AdvancedImport(importdir, "advanced configuration", client)
