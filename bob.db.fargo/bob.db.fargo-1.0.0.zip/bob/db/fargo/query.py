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
               protocol='mc-rgb'):
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
      Extension of anootation files

    """
    super(Database, self).__init__(SQLITE_FILE, File, original_directory, original_extension)
    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension
    self.protocol = protocol

  @property
  def modalities(self):
    return ['rgb', 'nir', 'depth']

  def groups(self, protocol=None):     
    """Returns the names of all registered groups
    
    Parameters
    ----------
    protocol: str
      ignored, since the group are the same across protocols.
    
    """   
    return ProtocolPurpose.group_choices


  def clients(self, protocol=None, groups=None):
    """Returns a set of clients for the specific query by the user.

    Parameters
    ----------
    protocol: str
      Ignored since the clients are identical for all protocols.
    groups: str or tuple of str
      The groups to which the clients belong ('world', 'dev', 'eval').

    Returns: 
    lst: 
      list containing clients which have the given properties.
    
    """

    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    retval = []
    if "world" in groups:
      q = self.query(Client).filter(Client.group == 'world')
      retval += list(q)
    if 'dev' in groups:
      q = self.query(Client).filter(Client.group == 'dev')
      retval += list(q)
    if 'eval' in groups:
      q = self.query(Client).filter(Client.group == 'eval')
      retval += list(q)
    return retval


  def models(self, protocol=None, groups=None):
    """Returns a set of models for the specific query by the user.

    Parameters
    ----------
    protocol
      Ignored since the models are identical for all protocols.
    groups
      The groups to which the subjects attached to the models belong

    Returns
    -------
    lst:
      A list containing all the models which have the given properties.
    """
    return self.clients(protocol, groups)


  def model_ids(self, protocol=None, groups=None):
    """Returns a set of models ids for the specific query by the user.

    Parameters
    ----------
    protocol
      Ignored since the models are identical for all protocols.
    groups
      The groups to which the subjects attached to the models belong

    Returns
    -------
    lst: 
      A list containing all the models ids which have the given properties.
    
    """
    return [model.id for model in self.models(protocol, groups)]


  def client(self, id):
    """Returns the client object of the specified id.
  
    Parameters
    ----------
    id: int
      The client id.
   
    Raises
    ------
    Error:
      if the client does not exist.
    
    """
    return self.query(Client).filter(Client.id == id).one()
 

  def protocol_names(self):
    """Returns all registered protocol names
    
    """
    l = self.protocols()
    retval = [str(k.name) for k in l]
    return retval


  def protocols(self):
    """Returns all registered protocols
    
    """
    return list(self.query(Protocol))

  
  def purposes(self):
    """Returns purposes 
    
    """
    return ProtocolPurpose.purpose_choices


  def objects(self, protocol=None, purposes=None, model_ids=None, groups=None, modality=None):
    """Returns a set of Files for the specific query by the user.

    Parameters
    ----------
    protocol: str
      One of the FARGO protocols.
    purposes: str or tuple of str
      The purposes required to be retrieved ('enroll', 'probe', 'train') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.
    model_ids: int or tuple of int
      Only retrieves the files for the provided list of model ids. 
      If 'None' is given, no filter over the model_ids is performed.
    groups: str or tuple of str
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.
    modality: str or tuple
      One of the three modalities 'rgb', 'nir' and 'depth'

    Returns
    -------
    lst:
      A list of files which have the given properties.
    
    """
    from sqlalchemy import and_
    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    modality = self.check_parameters_for_validity(modality, "modality", self.modalities)

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids, collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    if 'world' in groups:
      q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol)
      q = q.filter(Client.group == 'world').filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.group == 'world'))
      if model_ids:
        q = q.filter(Client.id.in_(model_ids))
      q = q.order_by(File.client_id)
      q = q.filter(File.modality.in_(modality))

      retval += list(q)

    if ('dev' in groups or 'eval' in groups):

      if('enroll' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.group.in_(groups), ProtocolPurpose.purpose == 'enroll'))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id)
        retval += list(q)

      # dense probing -> don't filter by model_ids
      if('probe' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.group.in_(groups), ProtocolPurpose.purpose == 'probe'))
        q = q.order_by(File.client_id)
        retval += list(q)

    # remove duplicates and sort the list
    rv = list(set(retval))
    rv.sort()
    return rv
