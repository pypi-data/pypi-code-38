#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Fri 3 Feb 13:43:22 2017

"""
  This is a high level interface for presentation attack ASVspoof2017 database.
  It is an extension of an interface defined inside bob.pad.base PAD framework.
"""

from bob.pad.voice.database import PadVoiceFile
from bob.pad.base.database import PadDatabase


class ASVspoof2017PadFile(PadVoiceFile):
    def __init__(self, f):
        """
        Initializes this File object with an File equivalent from the underlying SQl-based interface for
        ASVspoof2017 database.
        """
        attacktype = None
        if f.is_attack():
            attacktype = str(f.attacktype)

        super(ASVspoof2017PadFile, self).__init__(client_id=f.client_id, path=f.path, attack_type=attacktype, file_id=f.id)

        self.__f = f


class ASVspoof2017PadDatabase(PadDatabase):
    """
    Implements verification API for querying ASVspoof2017 database.
    """

    def __init__(self, protocol='competition', **kwargs):
        # call base class constructors to open a session to the database
        PadDatabase.__init__(self, name='asvspoof2017', protocol=protocol, **kwargs)

        from bob.db.asvspoof2017.query import Database as LowLevelDatabase
        self.__db = LowLevelDatabase()


    def convert_purposes(self, names, low_level_names, high_level_names):
        """
        Converts purposes names from a low level to high level API

        """

        if names is None:
            return None
        mapping = dict(zip(high_level_names, low_level_names))
        if isinstance(names, str):
            return mapping.get(names)
        return [mapping[g] for g in names]

    def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, **kwargs):
        """Returns a set of Files for the specific query by the user.

        Keyword Parameters:

        groups
            One of the groups ('dev', 'eval', 'train') or a tuple with several of them.
            If 'None' is given (this is the default), it is considered the same as a
            tuple with all possible values.

        protocol
          The protocol for which the clients should be retrieved.
          The protocol is dependent on your database.
          If you do not have protocols defined, just ignore this field.

        purposes
            The purposes can be either 'real' or 'attack'.

        model_ids
            This parameter is not supported in this implementation.


        Returns: A set of Files with the specified properties.
        """
        purposes = self.convert_purposes(purposes, ('genuine', 'spoof'), ('real', 'attack'))

        if protocol == 'largetrain':
            # this configuration is for ASVspoof2017 compettiion
            if 'train' in groups and 'dev' in groups:
                groups = ('train', 'dev', 'eval')
            elif 'train' in groups:
                groups = ('train', 'dev')
            elif 'dev' in groups:
                groups = ('eval',)

        objects = self.__db.objects(protocol=protocol, groups=groups, purposes=purposes, **kwargs)
        return [ASVspoof2017PadFile(f) for f in objects]
