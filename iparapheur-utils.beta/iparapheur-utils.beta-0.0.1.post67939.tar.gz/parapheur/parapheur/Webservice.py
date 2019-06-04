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
import mimetypes
import subprocess
import sys

import os
import requests
from requests.exceptions import SSLError
from suds.cache import NoCache
from suds.client import Client as Sudsclient
from suds.plugin import MessagePlugin, DocumentPlugin
from suds.transport import Reply
from suds.transport.https import HttpAuthenticated

import pprint

req_version = (3, 0)
cur_version = sys.version_info

if cur_version >= req_version:
    from io import StringIO
else:
    # noinspection PyCompatibility
    from StringIO import StringIO

__author__ = 'lhameury'


class RequestsTransport(HttpAuthenticated):
    def __init__(self, **kwargs):
        self.cert = kwargs.pop('cert', None)
        self.username = kwargs.pop('username', None)
        self.password = kwargs.pop('password', None)
        # super won't work because not using new style class
        HttpAuthenticated.__init__(self, **kwargs)

    def open(self, request):
        """
        Fetches the WSDL using cert.
        :param request: The request object
        """
        self.addcredentials(request)
        if "https" in request.url:
            resp = requests.get(request.url, data=request.message,
                                headers=request.headers, cert=self.cert, verify=False,
                                auth=(self.username, self.password))
        else:
            resp = requests.get(request.url, data=request.message,
                                headers=request.headers)
        result = StringIO(resp.content)
        return result

    def send(self, request):
        # Dirty hack... can not be handled in filter ! BEGIN
        request.message = request.message.replace("contentType", "xm:contentType")
        # END
        self.addcredentials(request)
        resp = requests.post(request.url, data=request.message,
                             headers=request.headers, cert=self.cert, verify=False,
                             auth=(self.username, self.password))
        result = Reply(resp.status_code, resp.headers, resp.content)
        return result


class Filter(MessagePlugin):
    def __init__(self):
        pass

    def marshalled(self, context):
        context.envelope.set('xmlns:xm', 'http://www.w3.org/2005/05/xmlmime')

    def received(self, context):
        reply = context.reply
        context.reply = reply[reply.find("<?xml version"):reply.rfind(">") + 1]


class Handlewsdl(DocumentPlugin):
    def __init__(self):
        pass

    def loaded(self, context):
        # Dirty hack ! Le type DossierID bloque !
        context.document = context.document.replace('type="iph:DossierID"', 'type="xsd:string"')


class Webservice:
    def __init__(self, config, user=None, password=None):
        pprint.log("\n[Parapheur-SOAP]", True)
        # Nom d'utilistaeur
        self.username = user if user is not None else config.get("Parapheur", "username")
        # Mot de passe utilisateur
        self.__password = password if password is not None else config.get("Parapheur", "password")
        # URL webservice
        self.__url = "https://" + config.get("Parapheur", "server") + "/ws-iparapheur"
        # Hostname
        self.__hostname = config.get("Parapheur", "server")
        pprint.info("Serveur     : " + self.__url)
        # Certificat webservice
        self.__cert = (
            os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', "files/public.pem"),
            os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', "files/private.pem"))

        # On vérifie que l'AC est fournie
        autoritypath = os.path.join('/tmp', 'autority.pem')
        # Si non, on récupère la chaîne via une commande openssl
        if not os.path.isfile(autoritypath):
            command = "echo \"\" | " \
                      "openssl s_client -showcerts -connect " + self.__hostname + ":443 2>/dev/null | " \
                                                                                  "sed -n -e '/BEGIN\\ CERTIFICATE/,/END\\ CERTIFICATE/ p'"
            p = subprocess.Popen(command,
                                 shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            aut = p.stdout.read()
            with open(autoritypath, "w") as text_file:
                text_file.write(aut)

        os.environ['REQUESTS_CA_BUNDLE'] = autoritypath

        pprint.info("Utilisateur : " + self.username)

        if os.path.isfile(self.__cert[0]):
            credentials = dict(username=self.username,
                               password=self.__password,
                               cert=self.__cert)
            t = RequestsTransport(**credentials)
            try:
                self.api = Sudsclient(self.__url + '?wsdl', plugins=[Handlewsdl(), Filter()],
                                      location=self.__url, transport=t, cache=NoCache())
                self.api.service.echo("Coucou, ici Python !")
                pprint.success("OK", True)
            except SSLError as e:
                print(e)
        else:
            pprint.error("Fichier {0} introuvable".format(self.__cert), True)

    def call(self):
        return self.api.service

    def listmethods(self):
        return self.api

    def create(self, objectname):
        return self.api.factory.create(objectname)

    @staticmethod
    def loaddocument(chunk_size, location):
        base64file = ""
        with open(location, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if data:
                    base64file += base64.b64encode(data)
                else:
                    break
        return base64file

    def loadsig(self, location):
        loadedfile = self.create("TypeDoc")
        loadedfile["value"] = self.loaddocument(8192, location)
        loadedfile["_contentType"] = "application/pkcs7-signature"
        return loadedfile

    def loadfile(self, location):
        loadedfile = self.create("TypeDoc")
        loadedfile["value"] = self.loaddocument(8192, location)
        loadedfile["_contentType"] = mimetypes.guess_type(location)[0]
        return loadedfile

    def loadannexefile(self, location, name, mimetype="UTF-8"):
        annexes = self.create("TypeDocAnnexes")
        annexe = self.create("DocAnnexe")
        annexe["nom"] = name
        annexe["fichier"] = self.loadfile(location)
        annexe["mimetype"] = mimetypes.guess_type(location)[0]
        annexe["encoding"] = mimetype
        annexe["signature"] = None
        annexes["DocAnnexe"] = [annexe]
        return annexes
