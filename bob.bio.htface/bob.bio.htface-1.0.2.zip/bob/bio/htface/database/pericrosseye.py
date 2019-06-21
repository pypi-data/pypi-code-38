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
from bob.bio.base.database import BioDatabase, BioFile
import bob.io.base


class PeriCrossEyeBioFile(FaceBioFile):

    def __init__(self, f):
        super(PeriCrossEyeBioFile, self).__init__(client_id=f.client_id, path=f.path, file_id=f.id)
        self.f = f


class PeriCrossEyeBioDatabase(BioDatabase):
    """
    Implements verification API for querying Pola_Thermal database.
    """

    def __init__(
            self,
            **kwargs
    ):
        # call base class constructors to open a session to the database
        super(PeriCrossEyeBioDatabase, self).__init__(name='cross-eye-VIS-NIR-split1', **kwargs)

        from bob.db.pericrosseye.query import Database as LowLevelDatabase
        self.db = LowLevelDatabase()

    def model_ids_with_protocol(self, groups=None, protocol="cross-eye-VIS-NIR-split1", **kwargs):
        return self.db.model_ids(groups=groups, protocol=protocol)

    def objects(self, groups=None, protocol="cross-eye-VIS-NIR-split1", purposes=None, model_ids=None, **kwargs):
        retval = self.db.objects(groups=groups, protocol=protocol, purposes=purposes, model_ids=model_ids, **kwargs)
        return [PeriCrossEyeBioFile(f) for f in retval]

    def annotations(self, file_object):
        return None

    @property
    def reproducible_protocols(self):
        """
        Those are the protocols used in the publications
        """
        return ["cross-eye-VIS-NIR-split1", "cross-eye-VIS-NIR-split2", "cross-eye-VIS-NIR-split3",
                "cross-eye-VIS-NIR-split4", "cross-eye-VIS-NIR-split5"]

        
