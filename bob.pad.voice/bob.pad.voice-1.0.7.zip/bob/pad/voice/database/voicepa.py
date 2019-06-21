#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Tue 11 Oct 15:43:22 2016

"""
  This is a high level interface for presentation attack voicePA database.
  It is an extension of an interface defined inside bob.pad.base PAD framework.
"""

from bob.pad.voice.database import PadVoiceFile
from bob.pad.base.database import PadDatabase


class VoicePAPadFile(PadVoiceFile):
    def __init__(self, f):
        """
        Initializes this File object with a File equivalent from the underlying SQl-based interface for
        voicePA database.
        """
        attacktype = None
        if f.is_attack():
            attacktype = str(f.get_attack())

        super(VoicePAPadFile, self).__init__(client_id=f.client_id, path=f.path, attack_type=attacktype, file_id=f.id)

        self.__f = f


class VoicePAPadDatabase(PadDatabase):
    """
    Implements verification API for querying voicePA database.
    """

    def __init__(self, protocol='grandtest', **kwargs):
        # call base class constructors to open a session to the database
        PadDatabase.__init__(self, name='voicepa', protocol=protocol, **kwargs)

        from bob.db.voicepa.query import Database as LowLevelDatabase
        self.__db = LowLevelDatabase()

        # Since the high level API expects different group names than what the low
        # level API offers, you need to convert them when necessary
        # self.low_level_group_names = ('train', 'dev', 'eval')
        # self.high_level_group_names = ('train', 'dev', 'eval')

    def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, **kwargs):
        """Returns a set of Files for the specific query by the user.

        Keyword Parameters:

        groups
            One of the groups ('train', 'dev', 'eval') or a tuple with several of them.
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
        # we do not need to convert group names, since we have the same ('train', 'dev', 'eval') names as
        # high level API
        # matched_groups = self.convert_names_to_lowlevel(
        #     groups, self.low_level_group_names, self.high_level_group_names)

        objects = self.__db.objects(protocol=protocol, groups=groups, cls=purposes, **kwargs)
        return [VoicePAPadFile(f) for f in objects]
