#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Sat 20 Aug 15:43:10 CEST 2016

"""
  CUHK_CUFS database implementation of bob.bio.base.database.ZTDatabase interface.
  It is an extension of an SQL-based database interface, which directly talks to CUHK_CUFS database, for
  verification experiments (good to use in bob.bio.base framework).
"""

from bob.bio.face.database import FaceBioFile
from bob.bio.base.database import ZTBioDatabase, BioFile
import bob.io.base


class NIVLBioFile(FaceBioFile):

    def __init__(self, f, db):
        super(NIVLBioFile, self).__init__(client_id=f.client_id, path=f.path, file_id=f.id)
        self.f = f
        self.db = db

    @property
    def modality(self):
        return self.f.modality


class NIVLBioDatabase(ZTBioDatabase):
    """
    Implements verification API for querying CUHK_CUFS database.
    """

    def __init__(
            self,
            **kwargs
    ):
        # call base class constructors to open a session to the database
        super(NIVLBioDatabase, self).__init__(name='nivl', **kwargs)

        from bob.db.nivl.query import Database as LowLevelDatabase
        self.db = LowLevelDatabase()

    def model_ids_with_protocol(self, groups=None, protocol="idiap-search_VIS-NIR_split1", **kwargs):
        return self.db.model_ids(groups=groups, protocol=protocol)

    def tmodel_ids_with_protocol(self, protocol="idiap-search_VIS-NIR_split1", groups=None, **kwargs):
        return self.db.tmodel_ids(protocol=protocol, groups=groups, **kwargs)

    def objects(self, groups=None, protocol="idiap-search_VIS-NIR_split1", purposes=None, model_ids=None, **kwargs):
        retval = self.db.objects(groups=groups, protocol=protocol, purposes=purposes, model_ids=model_ids, **kwargs)
        return [NIVLBioFile(f, self.db) for f in retval]

    def tobjects(self, groups=None, protocol="idiap-search_VIS-NIR_split1", model_ids=None, **kwargs):
        retval = self.db.tobjects(groups=groups, protocol=protocol, model_ids=model_ids, **kwargs)
        return [NIVLBioFile(f, self.db) for f in retval]

    def zobjects(self, groups=None, protocol="idiap-search_VIS-NIR_split1", **kwargs):
        retval = self.db.zobjects(groups=groups, protocol=protocol, **kwargs)
        return [NIVLBioFile(f, self.db) for f in retval]

    def annotations(self, file_object):
        return file_object.f.annotations()

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
        return ["idiap-search_VIS-NIR_split1", "idiap-search_VIS-NIR_split2", "idiap-search_VIS-NIR_split3",
                "idiap-search_VIS-NIR_split4", "idiap-search_VIS-NIR_split5"]

