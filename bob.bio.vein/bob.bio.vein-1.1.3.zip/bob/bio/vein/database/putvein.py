# vim: set fileencoding=utf-8 :

"""
PUTVEIN database implementation of bob.bio.db.BioDatabase interface.
It is an extension of low level database interface, which directly talks to
PUTVEIN database for verification experiments (good to use in bob.bio.base
framework).
"""

from bob.bio.base.database import BioFile, BioDatabase
import bob.ip.color
import numpy as np


class File(BioFile):
    """
    Implements extra properties of vein files for the PUTVEIN database

    Parameters:

      f (object): Low-level file (or sample) object that is kept inside
    """
    def __init__(self, f):
        super(File, self).__init__(client_id=f.client_id,
                                   path=f.path,
                                   file_id=f.id)

        self.f = f

    def load(self, directory=None, extension='.bmp'):
        """
        The image returned by the ``bob.db.putvein`` is RGB (with shape
        (3, 768, 1024)). This method converts image to a greyscale (shape
        (768, 1024)) and then rotates image by 270 deg so that images can be
        used with ``bob.bio.vein`` algorythms designed for the
        ``bob.db.biowave_v1`` database.
        Output images dimentions - (1024, 768).
        """
        color_image = self.f.load(directory=directory,
                                  extension=extension)
        grayscale_image = bob.ip.color.rgb_to_gray(color_image)
        grayscale_image = np.rot90(grayscale_image, k=3)
        return grayscale_image


class PutveinBioDatabase(BioDatabase):
    """
    Implements verification API for querying PUTVEIN database.
    This class allows to use the following protocols:

    palm-L_1
    palm-LR_1
    palm-R_1
    palm-RL_1
    palm-R_BEAT_1

    palm-L_4
    palm-LR_4
    palm-R_4
    palm-RL_4
    palm-R_BEAT_4

    wrist-L_1
    wrist-LR_1
    wrist-R_1
    wrist-RL_1
    wrist-R_BEAT_1

    wrist-L_4
    wrist-LR_4
    wrist-R_4
    wrist-RL_4
    wrist-R_BEAT_4
    """

    def __init__(self, **kwargs):

        super(PutveinBioDatabase, self).__init__(name='putvein', **kwargs)

        from bob.db.putvein.query import Database as LowLevelDatabase
        self.__db = LowLevelDatabase()

        self.low_level_group_names = ('train', 'dev', 'eval')
        self.high_level_group_names = ('world', 'dev', 'eval')

    def groups(self):

        return self.convert_names_to_highlevel(self.__db.groups(),
            self.low_level_group_names, self.high_level_group_names)

    def __protocol_split__(self, prot_name):
        """
        Overrides the "high level" database names (see the list abowe) to the
        low level ``protocols`` (currently there are 8 low level protocols:
            L_1;
            LR_1;
            R_1;
            RL_1;
            R_BEAT_1;
            L_4;
            LR_4;
            R_4;
            RL_4;
            R_BEAT_4;
        And the kinds - wrist or palm.
        The low level protocols are derived from the original 4:
            L;
            R;
            LR;
            RL;
        please read the ``bob.db.putvein`` documentation.
        """
        allowed_prot_names = ["palm-L_1",
                              "palm-LR_1",
                              "palm-R_1",
                              "palm-RL_1",
                              "palm-R_BEAT_1",
                              "palm-L_4",
                              "palm-LR_4",
                              "palm-R_4",
                              "palm-RL_4",
                              "palm-R_BEAT_4",
                              "wrist-L_1",
                              "wrist-LR_1",
                              "wrist-R_1",
                              "wrist-RL_1",
                              "wrist-R_BEAT_1",
                              "wrist-L_4",
                              "wrist-LR_4",
                              "wrist-R_4",
                              "wrist-RL_4",
                              "wrist-R_BEAT_4"]

        if prot_name not in allowed_prot_names:
            raise IOError("Protocol name {} not allowed. Allowed names - {}".\
                          format(prot_name, allowed_prot_names))

        kind, prot = prot_name.split("-")

        return kind, prot

    def client_id_from_model_id(self, model_id, group='dev'):
        """Required as ``model_id != client_id`` on this database"""
        return self.__db.client_id_from_model_id(model_id)


    def model_ids_with_protocol(self, groups=None, protocol=None, **kwargs):
        """model_ids_with_protocol(groups = None, protocol = None, **kwargs) -> ids

        Returns a list of model ids for the given groups and given protocol.

        **Parameters:**

        groups : one or more of ``('world', 'dev', 'eval')``
          The groups to get the model ids for.

        protocol: a protocol name

        **Returns:**

        ids : [int]
          The list of (unique) model ids for the given groups.
        """
        kind, prot = self.__protocol_split__(protocol)

        groups = self.convert_names_to_lowlevel(groups, self.low_level_group_names, self.high_level_group_names)

        return self.__db.model_ids(protocol=prot,
                                   groups=groups,
                                   kinds=kind)


    def objects(self, protocol=None, groups=None, purposes=None, model_ids=None, kinds=None, **kwargs):

        kind, prot = self.__protocol_split__(protocol)

        groups = self.convert_names_to_lowlevel(groups, self.low_level_group_names, self.high_level_group_names)

        retval = self.__db.objects(protocol=prot,
                                   groups=groups,
                                   purposes=purposes,
                                   model_ids=model_ids,
                                   kinds=kind)
        return [File(f) for f in retval]


    def annotations(self, file):
        return None


