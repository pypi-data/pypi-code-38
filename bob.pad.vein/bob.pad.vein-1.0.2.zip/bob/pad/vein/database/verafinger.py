#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy
from bob.pad.base.database import PadFile, PadDatabase


class VerafingerPadFile(PadFile):
  """High-level implementation of Files for the Verafinger database
  """

  def __init__(self, f):
    self.f = f
    super(VerafingerPadFile, self).__init__(client_id=f.finger.unique_name,
        path=f.path, attack_type=None if f.source == 'bf' else 'attack',
        file_id=f.id)


class VerafingerPadDatabase(PadDatabase):
  """High-level implementation for the Verafinger database

  Parameters
  ----------

  kwargs
      The arguments of the :py:class:`bob.bio.base.database.BioDatabase` base
      class constructor.

  """

  def __init__(self, **kwargs):
    from bob.db.verafinger import PADDatabase as LowLevelDatabase
    self.db = LowLevelDatabase()
    super(VerafingerPadDatabase, self).__init__(name='verafinger', **kwargs)


  def objects(self, groups=None, protocol=None, purposes=None, model_ids=None,
      **kwargs):
    """Lists VerafingerPadFile objects, which fulfill the given restrictions.

    Parameters
    ----------
    groups : :obj:`str` or [:obj:`str`]
        The groups of which the clients should be returned.
        Usually, groups are one or more elements of
        ('train', 'dev', 'eval')

    protocol : str
        The protocol for which the clients should be retrieved.
        The protocol is dependent on your database.
        If you do not have protocols defined, just ignore this field.

    purposes : :obj:`str` or [:obj:`str`]
        The purposes for which VerafingerPadFile objects should be retrieved.
        Usually it is either 'real' or 'attack'.

    model_ids
        This parameter is not supported in PAD databases yet
    **kwargs

    Returns
    -------
    files : [VerafingerPadFile]
        A list of VerafingerPadFile objects.
    """

    files = self.db.objects(protocol=protocol, groups=groups,
        purposes=purposes, **kwargs)
    return [VerafingerPadFile(f) for f in files]


  def annotations(self, f):
    return None
