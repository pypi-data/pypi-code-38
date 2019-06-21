#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Sat 20 Aug 15:43:10 CEST 2016


from bob.bio.face.database import FaceBioFile
from bob.bio.base.database import ZTBioDatabase, BioFile
import bob.io.base
import os


class CBSR_NIR_VIS_2BioFile(FaceBioFile):

    def __init__(self, f, db):
        super(CBSR_NIR_VIS_2BioFile, self).__init__(client_id=f.client_id, path=f.path, file_id=f.id)
        self.f = f
        self.db = db
        
        
    def make_path(self, original_directory, original_extension=None):
        if isinstance(original_extension, list):
            for o in original_extension:
                file_name = os.path.join(original_directory, self.path + o)
                if os.path.exists(file_name):
                    return str(file_name)
            raise ValueError("File {0} not found".format(str(file_name)))
        else:
            return super(FaceBioFile, self).make_path(original_directory, original_extension)


    @property
    def modality(self):
        return self.f.modality


class CBSR_NIR_VIS_2BioDatabase(ZTBioDatabase):
    """
    Implements verification API for querying CBSR_NIR_VIS_2 database.
    """

    def __init__(
            self,
            **kwargs
    ):
        # call base class constructors to open a session to the database
        super(CBSR_NIR_VIS_2BioDatabase, self).__init__(name='CBSR_NIR_VIS_2', **kwargs)

        from bob.db.cbsr_nir_vis_2.query import Database as LowLevelDatabase
        self.db = LowLevelDatabase()

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
        return ["view2_1", "view2_2", "view2_3", "view2_4", "view2_5"]

    def model_ids_with_protocol(self, groups=None, protocol="view2_1", **kwargs):
        return self.db.model_ids(groups=groups, protocol=protocol)

    def tmodel_ids_with_protocol(self, protocol="view2_1", groups=None, **kwargs):
        return self.db.tmodel_ids(protocol=protocol, groups=groups, **kwargs)

    def objects(self, groups=None, protocol="view2_1", purposes=None, model_ids=None, **kwargs):
        retval = self.db.objects(groups=groups, protocol=protocol, purposes=purposes, model_ids=model_ids, **kwargs)
        return [CBSR_NIR_VIS_2BioFile(f, self.db) for f in retval]

    def tobjects(self, groups=None, protocol="view2_1", model_ids=None, **kwargs):
        retval = self.db.tobjects(groups=groups, protocol=protocol, model_ids=model_ids, **kwargs)
        return [CBSR_NIR_VIS_2BioFile(f, self.db) for f in retval]

    def zobjects(self, groups=None, protocol="view2_1", **kwargs):
        retval = self.db.zobjects(groups=groups, protocol=protocol, **kwargs)
        return [CBSR_NIR_VIS_2BioFile(f, self.db) for f in retval]

    def annotations(self, file_object):
        return file_object.f.annotations()
        
