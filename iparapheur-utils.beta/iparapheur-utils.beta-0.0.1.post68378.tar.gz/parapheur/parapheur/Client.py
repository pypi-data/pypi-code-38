# coding=utf-8
# module Parapheur
"""
CeCILL Copyright (c) 2006-2015, ADULLACT-projet
Initiated by ADULLACT-projet S.A.
Developped by ADULLACT-projet S.A.

contact@adullact-projet.coop

Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
sur le site "http://www.cecill.info".

En contrepartie de l'accessibilité au code source et des droits de copie,
de modification et de redistribution accordés par cette licence, il n'est
offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
seule une responsabilité restreinte pèse sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les concédants successifs.

A cet égard  l'attention de l'utilisateur est attirée sur les risques
associés au chargement,  à l'utilisation,  à la modification et/ou au
développement et à la reproduction du logiciel par l'utilisateur étant
donné sa spécificité de logiciel libre, qui peut le rendre complexe à
manipuler et qui le réserve donc à des développeurs et des professionnels
avertis possédant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
logiciel à leurs besoins dans des conditions permettant d'assurer la
sécurité de leurs systèmes et ou de leurs données et, plus généralement,
à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.

Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
pris connaissance de la licence CeCILL, et que vous en avez accepté les
termes.
"""
import base64
import importlib
import sys

import os
import requests

import pprint

req_version = (3, 0)
cur_version = sys.version_info
isp3 = cur_version >= req_version

if isp3:
    # noinspection PyCompatibility
    from configparser import NoOptionError, NoSectionError
else:
    # noinspection PyCompatibility
    # noinspection PyCompatibility
    from ConfigParser import NoOptionError, NoSectionError

__author__ = 'lhameury'


# Handle login and curl requests
class Client:
    def runas(self, username):
        """
        Permet l'utilisation du client en tant qu'un utilisateur différent
        :param username: Nom d'utilisateur, celui-ci doit déjà être authentifié
        :return: Rien
        """
        if username not in self.__ticketlist:
            raise NotAuthenticatedError("Utilisateur {0} non authentifié !".format(username))
        elif username in self.__ticketlist and self.loggedAs != username:
            self.__ticket = self.__ticketlist[username]
            self.loggedAs = username
            pprint.header("Run as: '{0}'".format(username), False)

    def login(self, user, passw):
        """
        Récupération d'un ticket d'authentification pour l'utilisateur donné.
        Ce ticket est conservé en cas d'authentification avec un autre utilisateur.
        Il peut ensuite être ré-authentifié via la fonction 'runas'
        :param user: Nom d'utilisateur
        :param passw: Password
        :return: Rien
        """
        if user not in self.__ticketlist:
            pprint.info("Connexion   : {0} ".format(user), False, '')

            r = requests.post("{0}://{1}/alfresco/wcs/parapheur/api/login".format(self.__schema, self.server),
                              json=({'username': user, 'password': passw}), verify=False)

            if r.status_code == 200:
                json_response = r.json()
                # Le ticket est bien trouvé, on est connecté
                self.__ticket = json_response['data']['ticket']
                self.__ticketlist[user] = json_response['data']['ticket']
                self.islogged = True
                self.loggedAs = user
                pprint.success("OK".format(user), True)
            elif r.status_code == 403:
                json_response = r.json()
                pprint.error("KO - Erreur lors de la connexion: {0}".format(str(json_response['message'])), True)
            else:
                pprint.error("KO - Erreur inconnue :", True)
                print(r.text)
        else:
            self.runas(user)

    @staticmethod
    def load_class(full_class_string):
        """
        Chargement de classe automatique, à partir d'un chemin de classe
        Utilisé pour charger le module "API"
        :param full_class_string: Chaine de caractère représentant la classe à importer
        :return: La classe importée
        """
        class_data = full_class_string.split(".")
        module_path = ".".join(class_data[:-1])
        class_str = class_data[-1]

        module = importlib.import_module(module_path)
        # Finally, we retrieve the Class
        return getattr(module, class_str)

    @staticmethod
    def load_binary_file(filename):
        """
        Chargement d'un fichier binaire et conversion en Base64
        :param filename: Nom du fichier
        :return: Base64 du fichier
        """
        # use mode = "rb" to read binary file
        fin = open(filename, "rb")
        binary_data = fin.read()
        fin.close()
        # encode binary to base64 string (printable)
        return base64.b64encode(binary_data)

    def __getitem__(self, key):
        """
        Getter d'objet dans le dictionnaire
        """
        return self.__dict__[key]

    def __setitem__(self, key, value):
        """
        Setter d'objet dans le dictionnaire
        """
        self.__dict__[key] = value

    def __init__(self, config):
        """
        Fonction d'initialisation du module Parapheur.Client
        Authentification et mise en place des helpers d'API
        :param config:  Fichier de configuration,
                        doit comporter une section 'Parapheur' avec la valeur 'server' au minimum
        """
        pprint.log("\n[Parapheur-REST]", True)
        # Utilisateur log ?
        self.islogged = False
        try:
            # URL du serveur
            self.server = config.get("Parapheur", "server")
            pprint.info("Serveur     : " + self.server)
            # Ticket de connexion
            self.__ticketlist = {}
            self.__ticket = None
            self.loggedAs = None
            try:
                # Nom d'utilistaeur
                username = config.get("Parapheur", "username")
                pprint.info("Utilisateur : " + username)
                # Mot de passe utilisateur
                password = config.get("Parapheur", "password")
                # Autorité de certification - DISABLED
                # autority = config.get("Parapheur", "server_ac")
                # Récupération du chemin de l'AC
                # self.__autority = os.path.abspath(os.path.join(os.path.split(__file__)[0], os.pardir)) + '/' + autority
                self.__autority = ""
                # Set default schema
                try:
                    self.__schema = config.get("Parapheur", "schema")
                except NoOptionError:
                    self.__schema = "https"
                    pass
                # Login de l'utilisateur
                self.login(username, password)
            except NoOptionError:
                # Do nothing
                pass
        except (NoOptionError, NoSectionError) as e:
            pprint.error("Erreur fichier de configuration: {0}".format(str(e)), True)

    def __send(self, url, post, params, requesttype):
        """
        Envoi de requête vers le serveur d'API REST
        :param url: URL de requête
        :param post: Données POST
        :param params: Données GET
        :param requesttype: Type de requête (POST, GET, UPDATE, DELETE, ...)
        :return: Le résultat de la requête JSON, transformé en objet
        """
        # Handle parameters
        if not params:
            params = {}
        param_string = ""
        if isp3:
            for attr in params.keys():
                param_string += "&" + attr + "=" + params[attr]
        else:
            # noinspection PyCompatibility
            for attr in params.iterkeys():
                param_string += "&" + attr + "=" + params[attr]

        if post:
            post_data = post
        else:
            post_data = ()

        # Handle request
        r = requests.request(requesttype,
                             "{0}://{1}/alfresco/wcs{2}?ticket={3}{4}".format(self.__schema, self.server, url,
                                                                              self.__ticket, param_string),
                             json=post_data, verify=False)
        if r.status_code == 200:
            try:
                response = r.json()
            except:
                response = r.text
        else:
            response = False
        return response

    def dopost(self, url, post=None, params=None):
        return self.__send(url, post, params, "POST")

    def doput(self, url, post=None, params=None):
        return self.__send(url, post, params, "PUT")

    def doget(self, url, params=None):
        return self.__send(url, None, params, "GET")

    def dodelete(self, url, params=None):
        return self.__send(url, None, params, "DELETE")

    def dodownload(self, url, filename):
        with open(filename, 'wb') as handle:
            response = requests.get(
                "{0}://{1}/alfresco/wcs{2}?ticket={3}".format(self.__schema, self.server, url, self.__ticket),
                stream=True, verify=False)

            if not response.ok:
                pprint.error("Error when downloading file %s" % filename, True)

            for block in response.iter_content(chunk_size=1024):
                if block:  # filter out keep-alive new chunks
                    handle.write(block)

    def dodownloadfromnode(self, url, property, filename):
        with open(filename, 'wb') as handle:
            response = requests.get(
                "{0}://{1}/alfresco/d/d{2}?ticket={3}&property={4}".format(self.__schema, self.server, url,
                                                                           self.__ticket, property),
                stream=True, verify=False)

            if not response.ok:
                print(response)
                pprint.error("Error when downloading file %s" % filename, True)

            for block in response.iter_content(chunk_size=1024):
                if block:  # filter out keep-alive new chunks
                    handle.write(block)

    def getspacenoderef(self, tenant=None):
        """
        Récupération du NodeRef du "workspace://SpacesStore", avec prise en compte du tenant si besoin
        :param tenant: Tenant sur lequel récupérer le node. Si vide, récupération sur le tenant ROOT
        :return: Le NodeRef du noeud
        """
        return self.doget(
            "/slingshot/doclib/treenode/node/alfresco/company/home/",
            {"children": "false",
             "libraryRoot": "alfresco://company/home",
             "max": "500"})['parent']['nodeRef']

    def executescript(self, scriptfile, *args, **kwargs):
        """
        Execution de script javascript via l'API REST

        :param scriptfile:  Fichier JS à exécuter
        :param kwargs:      runas: Execution en tant qu'utilisateur fourni
                            format: String à intégrer dans le script. Dans le fichier JS,
                                    remplacement des '{n}' (même principe que 'format')

        :return:            Résultat de la requête
        """
        # pprint.header("Exec: '{0}'".format(scriptfile, runas))
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "scripts", "javascript",
                               scriptfile)) as script:
            scriptdata = script.read()
        return self.dopost("/de/fme/jsconsole/execute",
                           {"context": {},
                            "documentNodeRef": "",
                            "runas": kwargs.get("runas", self.loggedAs),
                            "script": scriptdata.format(*kwargs.get("format")) if kwargs.get("format") else scriptdata,
                            "spaceNodeRef": self.getspacenoderef(kwargs.get("tenant", "")),
                            "template": "",
                            "transaction": True,
                            "urlargs": ""})


class NotAuthenticatedError(Exception):
    """
    Custom exception pour problème d'authentification via l'API
    """
    pass
