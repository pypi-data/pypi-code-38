#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""
  LDHF database implementation of bob.bio.base.database.Database interface.
  It is an extension of an SQL-based database interface, which directly talks to LDHF database, for
  verification experiments (good to use in bob.bio.base framework).
"""

import os
import bob.db.base

from bob.bio.face.database import FaceBioFile
from bob.bio.base.database import BioDatabase


class LDHFBioFile(FaceBioFile):

    def __init__(self, f, db):
        super(LDHFBioFile, self).__init__(client_id=f.client_id, path=f.path, file_id=f.id)
        self.f = f
        self.db = db

    @property
    def modality(self):
        return self.f.modality


class LDHFBioDatabase(BioDatabase):
    """
    LDHF database implementation of :py:class:`bob.bio.base.database.BioDatabase` interface.
    """

    def __init__(
            self,
            original_directory=None,
            original_extension='.JPG',
            protocol='split1',
            **kwargs
    ):
        # call base class constructors to open a session to the database
        super(LDHFBioDatabase, self).__init__(
            name='ldhf',
            original_directory=original_directory,
            original_extension=original_extension,            
            **kwargs)

        from bob.db.ldhf.query import Database as LowLevelDatabase
        self.protocol = protocol
        self._db = LowLevelDatabase(original_directory, original_extension)

    def objects(self, groups=None, purposes=None, protocol=None, model_ids=None, **kwargs):
        retval = self._db.objects(protocol=protocol, groups=groups, purposes=purposes, model_ids=model_ids, **kwargs)
        return [LDHFBioFile(f, self._db) for f in retval]
    
    def model_ids_with_protocol(self, groups=None, protocol=None, **kwargs):
        return self._db.model_ids(groups=groups, protocol=protocol)

    def annotations(self, file):
        return file.f.annotations()
        
    @property
    def modality_separator(self):
        return self._db.modality_separator

    @property
    def modalities(self):
        return self._db.modalities

    @property
    def reproducible_protocols(self):
        """
        Those are the protocols used in the publications
        """
        return ["split1","split2","split3","split4","split5"]

