#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Sat 20 Aug 15:43:10 CEST 2016

"""
  EPRIP database implementation of bob.bio.base.database.ZTDatabase interface.
  It is an extension of an SQL-based database interface, which directly talks to EPRIP database, for
  verification experiments (good to use in bob.bio.base framework).
"""

from bob.bio.face.database import FaceBioFile
from bob.bio.base.database import BioDatabase, BioFile
import bob.io.base


class EPRIPBioFile(FaceBioFile):

    def __init__(self, f, db):
        super(EPRIPBioFile, self).__init__(client_id=f.client_id, path=f.path, file_id=f.id)
        self.f = f
        self.db  = db


    def load(self, directory=None, extension=""):
        return bob.io.base.load(self.db.original_file_name(self.f))


    def make_path(self, directory, extension=None):
        if isinstance(extension, list):
            #Hacking for the original data.
            # The load funtion knows how to load this
            return super(FaceBioFile, self).make_path(directory, extension[0])
        else:
            return super(FaceBioFile, self).make_path(directory, extension)


    @property
    def modality(self):
        return self.f.modality


class EPRIPBioDatabase(BioDatabase):
    """
    Implements verification API for querying EPRIP database.
    """

    def __init__(
            self,
            original_directory="",
            original_extension = ['.jpg'],
            **kwargs
    ):
        # call base class constructors to open a session to the database
        super(EPRIPBioDatabase, self).__init__(name='eprip', **kwargs)

        from bob.db.eprip.query import Database as LowLevelDatabase
        self.db = LowLevelDatabase(original_directory=original_directory,
                                   original_extension=original_extension
                                   )

        self.original_directory = original_directory
        self.original_extension = original_extension

                                   
    @property
    def modality_separator(self):
        return self.db.modality_separator

    @property
    def modalities(self):
        return self.db.modalities

    @property
    def reproducible_protocols(self):
        """
        Those are the protocols used in the publications
        """
        return ["search_split1_p2s", "search_split2_p2s", "search_split3_p2s",
                "search_split4_p2s", "search_split5_p2s"]

    def original_file_name(self, file, check_existence = True):
        return self.db.original_file_name(file, check_existence = check_existence)    

    def model_ids_with_protocol(self, groups=None, protocol="search_split1_p2s", **kwargs):
        return self.db.model_ids(groups=groups, protocol=protocol)
        
    def objects(self, groups=None, protocol="search_split1_p2s", purposes=None, model_ids=None, **kwargs):
        retval = self.db.objects(groups=groups, protocol=protocol, purposes=purposes, model_ids=model_ids, **kwargs)
        return [EPRIPBioFile(f, self.db) for f in retval]
        
    def annotations(self, file_object):
        return file_object.f.annotations()

