#!/usr/bin/env python
# coding=utf-8
# Author - lhameury@libriciel.coop - Libriciel SCOP

"""
Script permettant de traiter l'envoi via pushdoc de flux via un chemin du type :
/TYPE/SOUSTYPE/fichier.pdf

OU

/TYPE/SOUSTYPE/fichier.xml (xades)

OU

/TYPE/SOUSTYPE/Dossier/fichier.pdf
/TYPE/SOUSTYPE/Dossier/annexes/*
/TYPE/SOUSTYPE/Dossier/signature.xml / signature.p7s
-------------
Pré-requis :
- Un jar pushdoc en dernière version dans le même dossier que ce script
- Tout le nécéssaire pour faire fonctionner pushdoc (wsdl, conf.cf, keystore, truststore)
- Le fichier par défaut pour le visuel pdf des flux PES (template-visuelPDF.pdf)
"""

import os
import shutil
import subprocess
import json

from os.path import isfile, join, isdir
from parapheur.parapheur import config

import_dir = config.get("Pushdoc", "import_dir")
user_mail = config.get("Pushdoc", "user_mail")
default_xpath = config.get("Pushdoc", "default_xpath")
template_pdf_file = config.get("Pushdoc", "template_pdf_file")
jar_file = config.get("Pushdoc", "jar_file")


class FolderParsing:

    import_dir = None

    def __init__(self, dir_to_parse):
        self.import_dir = dir_to_parse
        self.push_all()

    @staticmethod
    def handle_path_with_result(path, result):
        file_path = os.path.basename(path)
        if result is None:
            print("Pas de résultat pour %s" % file_path)
        elif "soumis dans le circuit" in result:
            print("%s créé" % file_path)
            # Delete file or folder
            if isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        else:
            print("Erreur de creation du dossier %s : \n%s" % (file_path, result))

    def push_all(self):
        for type_paraph in os.listdir(self.import_dir):
            type_path = join(import_dir, type_paraph)
            for subtype_paraph in os.listdir(type_path):
                subtype_path = join(type_path, subtype_paraph)

                for file_paraph in os.listdir(subtype_path):
                    complete_path = join(subtype_path, file_paraph)
                    result = FileToSend(type_paraph, subtype_paraph, complete_path).send_to_paraph()
                    self.handle_path_with_result(complete_path, result)


class FileToSend:
    file_to_send = None
    signature = None
    annexes = None
    annexes_folder = None
    metadatas = None
    possible_xml_main_file = None
    forced_name = None
    is_pes = False

    def __init__(self, ptype, subtype, path):
        self.type = ptype
        self.subtype = subtype
        self.path = path
        self.construct()

    def handle_meta_file(self, path):
        """
        Transformation du fichier "metadata" en dictionnaire
        :param path: Chemin du fichier
        """
        self.metadatas = dict(l.rstrip().split('=') for l in open(path))

    def handle_sig_file(self, path):
        if "xml" in path:
            self.possible_xml_main_file = path
            # Les fichiers XML sont considérés comme des signatures XAdES détachées
            # Les fichiers P7S sont considérés comme des signatures PKCS#7
        self.signature = path

    def handle_annexes(self, path):
        self.annexes = dict()
        self.annexes_folder = os.path.basename(path)
        i = 1
        for annexe in os.listdir(path):
            self.annexes[str(i)] = annexe
            i += 1

    def construct(self):
        if isdir(self.path):  # Handle file with annexes and detached signature
            for subfile_paraph in os.listdir(self.path):
                subfile_path = join(self.path, subfile_paraph)
                if isfile(subfile_path) and ("xml" in subfile_paraph or "p7s" in subfile_paraph):
                    self.handle_sig_file(subfile_path)
                elif isfile(subfile_path) and "metadata" in subfile_paraph:
                    # Le fichier metadata contient la liste des métadonnées sous la forme "nom=valeur"
                    self.handle_meta_file(subfile_path)
                elif isfile(subfile_path):  # Handle main file
                    self.file_to_send = subfile_path
                elif isdir(subfile_path):  # Gestion du répertoire des annexes
                    self.handle_annexes(subfile_path)
            if self.file_to_send is None and self.possible_xml_main_file is not None:
                self.file_to_send = self.possible_xml_main_file
            self.forced_name = os.path.basename(self.path)
        else:
            self.file_to_send = self.path
            if os.path.splitext(self.file_to_send)[1] == ".xml":
                self.is_pes = True

    def send_to_paraph(self):
        if self.file_to_send is not None:
            docname = os.path.basename(self.file_to_send)

            bash_command = 'java -jar %s ' \
                           '-T "%s" ' \
                           '-V "CONFIDENTIEL" ' \
                           '-c conf.cf ' \
                           '-d "%s" ' \
                           '-e "%s" ' \
                           '-n "%s" ' \
                           '-t "%s" ' % (jar_file, self.type, self.file_to_send, user_mail, docname, self.subtype)

            # Définition du nom)
            if self.forced_name is None:
                self.forced_name = os.path.splitext(os.path.basename(self.file_to_send))[0]
            bash_command += '-N "%s" ' % self.forced_name

            # Ajout des annexes
            if self.annexes is not None:
                bash_command += ' -a \'%s\' ' % json.dumps(self.annexes, ensure_ascii=False)
                bash_command += ' -A "%s" ' % self.annexes_folder
            # Ajout de la signature détachée
            if self.signature is not None:
                bash_command += ' -s "%s" ' % self.signature
            # Ajout des métadonnées
            if self.metadatas is not None:
                bash_command += ' -m \'%s\' ' % json.dumps(self.metadatas, ensure_ascii=False)
            if self.is_pes:
                bash_command += ' -v "%s" ' % os.path.join(os.path.dirname(os.path.realpath(__file__)), template_pdf_file)
                bash_command += ' -x "%s" ' % default_xpath
            else:
                bash_command += ' -v "%s" ' % self.file_to_send

            try:
                output = subprocess.check_output(['bash', '-c', bash_command], stderr=subprocess.STDOUT, cwd=os.getcwd())
                return output
            except subprocess.CalledProcessError as e:
                return e.output
        else:
            print("Attention, dossier vide : %s" % self.path)
            return None


FolderParsing(import_dir)
