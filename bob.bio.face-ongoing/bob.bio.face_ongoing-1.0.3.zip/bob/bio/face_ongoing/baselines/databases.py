#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import pkg_resources
import os


class Databases(object):
    """
    Baseclass for all the database resources for this project
    
    The database should have:
      - Name
      - Config
      - Protocol
      - Groups
    """
    def __init__(self):
        self.name = ""
        self.config = ""
        self.protocols = []
        self.groups = []
        self.preprocessed_directory = None
        self.extracted_directory = None


class Mobio(Databases):

    def __init__(self):
        self.name = "mobio"
        self.config = "mobio-male"
        self.protocols = ["male"]
        self.groups = ["dev", "eval"]
        self.preprocessed_directory = None
        self.extracted_directory = None
  

class IJBA(Databases):

    def __init__(self):
        self.name = "ijba"
        self.config = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/databases/ijba.py")
        self.protocols = ["compare_split{0}".format(i) for i in range(1, 11)]
        self.groups = ["dev"]
        self.preprocessed_directory = os.path.join(self.protocols[0], "preprocessed")
        self.extracted_directory = os.path.join(self.protocols[0], "extracted")


class IJBB(Databases):

    def __init__(self):
        self.name = "ijbb"
        self.config = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/databases/ijbb.py")
        self.protocols = ["1:1"]
        self.groups = ["dev"]
        self.preprocessed_directory = os.path.join(self.protocols[0], "preprocessed")
        self.extracted_directory = os.path.join(self.protocols[0], "extracted")


class IJBC(Databases):

    def __init__(self):
        self.name = "ijbc"
        self.config = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/databases/ijbc.py")
        self.protocols = ["1:1"]
        self.groups = ["dev"]
        self.preprocessed_directory = os.path.join(self.protocols[0], "preprocessed")
        self.extracted_directory = os.path.join(self.protocols[0], "extracted")


class LFW(Databases):

    def __init__(self):
        self.name = "lfw"
        self.config = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/databases/lfw.py")
        self.protocols = ["fold{0}".format(i) for i in range(1, 11)]
        self.groups = ["eval"]
        self.preprocessed_directory = os.path.join(self.protocols[0], "preprocessed")
        self.extracted_directory = os.path.join(self.protocols[0], "extracted")


class CasiaWebface(Databases):

    def __init__(self):
        self.name = "casia_webface"
        self.config = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/databases/casia_webface.py")
        self.protocols = ["number-all-split1", "number-all-split2", "number-all-split3"]
        self.groups = ["dev"]
        self.preprocessed_directory = os.path.join(self.protocols[0], "preprocessed")
        self.extracted_directory = os.path.join(self.protocols[0], "extracted")

