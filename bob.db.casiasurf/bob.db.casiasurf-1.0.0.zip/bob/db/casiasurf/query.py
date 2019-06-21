#!/usr/bin/env python
# encoding: utf-8

import os
from bob.db.base import utils
from .models import *

from .driver import Interface
INFO = Interface()
SQLITE_FILE = INFO.files()[0]

import bob.db.base

class Database(bob.db.base.SQLiteDatabase):
  """ Class representing the database

  See parent class `:py:class:bob.db.base.SQLiteDatabase` for more details ...

  Attributes
  ----------
  original_directory: str
    Path where the database is stored
  original_extension: str
    Extension of files in the database 
  annotation_directory: str
    Path where the annotations are stored
  annotation_extension: str
    Extension of anootation files

  """

  def __init__(self, 
               original_directory=None, 
               original_extension=None,
               annotation_directory=None,
               annotation_extension=None,
               protocol='all'):
    """ Init function

    Parameters
    ----------
    original_directory: str
      Path where the database is stored
    original_extension: str
      Extension of files in the database 
    annotation_directory: str
      Path where the annotations are stored
    annotation_extension: str
      Extension of annotation files

    """
    super(Database, self).__init__(SQLITE_FILE, ImageFile, original_directory, original_extension)
    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension
    self.protocol = protocol

  def groups(self, protocol=None):     
    """Returns the names of all registered groups
    
    Parameters
    ----------
    protocol: str
      ignored, since the group are the same across protocols.
    
    """   
    return ProtocolPurpose.group_choices


  def purposes(self):
    """Returns purposes 
    
    """
    return ProtocolPurpose.purpose_choices


  def objects(self, purposes=None, groups=None):
    """Returns a set of Samples for the specific query by the user.
    
    Note that a sample may contain up to 3 modalities (color, infrared and depth)
    The protocol specifies which modality(ies) should be loaded

    Parameters
    ----------
    purposes: str or tuple of str
      The purposes required to be retrieved ('real', 'attack') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. 
    groups: str or tuple of str
      One of the groups ('dev', 'eval', 'train') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    Returns
    -------
    lst:
      A list of samples which have the given properties.
    
    """
    from sqlalchemy import and_
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())

    q = self.query(Sample)\
                       .join((ProtocolPurpose, Sample.protocolPurposes))\
                       .filter(ProtocolPurpose.group.in_(groups))\
                       .filter(ProtocolPurpose.purpose.in_(purposes))\
                       .order_by(Sample.id)

    retval = list(set(q))
    return list(set(retval))  
