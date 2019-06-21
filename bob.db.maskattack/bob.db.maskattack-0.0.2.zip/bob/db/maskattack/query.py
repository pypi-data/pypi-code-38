#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Nesli Erdogmus <nesli.erdogmus@idiap.ch>
# Mon 25 Feb 15:23:54 2013

"""This module provides the Dataset interface allowing the user to query the
replay attack database in the most obvious ways.
"""

from bob.db.base import SQLiteDatabase
from .models import *
from .driver import Interface
from numpy import random

INFO = Interface()

SQLITE_FILE = INFO.files()[0]

class Database(SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension=None):
    # opens a session to the database - keep it open until the end
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)




  def sets(self):
    """Returns the names of all registered sets"""
    return ProtocolPurpose.set_choices # Same as Client.set_choices for this database

  def clients(self, protocol=None, sets=None):
    """Returns a set of clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('verification',)

    sets
      The sets to which the clients belong ('world', 'dev', 'test')

    Returns: A list containing all the clients which have the given properties.
    """

    self.assert_validity()
    VALID_SETS = self.sets()
    sets_ = self.check_parameters_for_validity(sets, "set", VALID_SETS, VALID_SETS)
    # List of the clients
    q = self.query(Client).filter(Client.set.in_(sets_)).\
          order_by(Client.id)
    return list(q)
    
  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    self.assert_validity()
    return self.query(Client).filter(Client.id==id).count() != 0

  def protocols(self):
    """Returns all protocol objects.
    """

    self.assert_validity()
    return list(self.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""

    self.assert_validity()
    return self.query(Protocol).filter(Protocol.name==name).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    self.assert_validity()
    return self.query(Protocol).filter(Protocol.name==name).one()

  def protocol_names(self):
    """Returns all registered protocol names"""
    return [str(p.name) for p in self.protocols()]

  def protocol_purposes(self):
    """Returns all registered protocol purposes"""

    return list(self.query(ProtocolPurpose))

  def purposes(self):
    """Returns the list of allowed purposes"""

    return ProtocolPurpose.purpose_choices

  def fileID_to_clientID(self,id):
    """Returns the client ID of the given file ID"""
    
    q = self.query(File).filter(File.id==id)    
    return q[0].client_id
    
  def fileID_to_session(self,id):
    """Returns the client ID of the given file ID"""
    
    q = self.query(File).filter(File.id==id)    
    return q[0].session
    
  def fileID_to_shot(self,id):
    """Returns the client ID of the given file ID"""
    
    q = self.query(File).filter(File.id==id)    
    return q[0].shot

  def objects(self, protocol=None, purposes=None, client_ids=None, sets=None,
      classes=None, groups=None):
    """Returns a set of filenames for the specific query by the user.
    
    Keyword Parameters:

    protocol
    One of the 3DMAD protocols ('verification', '').

    purposes
    The purposes required to be retrieved ('enrol', 'probeReal', 'probeMask', 'train') or a tuple
    with several of them. If 'None' is given (this is the default), it is
    considered the same as a tuple with all possible values. This field is
    ignored for the data from the "world" set.

    model_ids
    Only retrieves the files for the provided list of model ids (claimed
    client id). The model ids are string. If 'None' is given (this is
    the default), no filter over the model_ids is performed.

    sets
    One of the sets ('world', 'dev', 'test') or a tuple with several of them.
    If 'None' is given (this is the default), it is considered the same as a
    tuple with all possible values.

    classes
    The classes (types of accesses) to be retrieved ('client', 'impostor')
    or a tuple with several of them. If 'None' is given (this is the
    default), it is considered the same as a tuple with all possible values.

    Returns: A list of files which have the given properties.
    """


    VALID_PROTOCOLS = self.protocol_names()
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", VALID_PROTOCOLS, VALID_PROTOCOLS)


    #protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    sets = self.check_parameters_for_validity(sets, "set", self.sets())
    classes = self.check_parameters_for_validity(classes, "class", ('client', 'impostor'))
    #client_ids = self.check_parameters_for_validity(client_ids, "client_id", range(1,18))

    VALID_IDS = list(range(1, 18))
    client_ids = self.check_parameters_for_validity(client_ids, "client_id", VALID_IDS, VALID_IDS)

    import collections
    if(client_ids is None):
      client_ids = VALID_IDS
    elif(not isinstance(client_ids,collections.Iterable)):
      client_ids = (client_ids,)

    # Now query the database
    q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
            filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.set.in_(sets), ProtocolPurpose.purpose.in_(purposes), Client.id.in_(client_ids)))
            
    if(('probeMask' in purposes) or ('probeReal' in purposes)):
        if(classes == 'client'):
            q = q.filter(Client.id.in_(client_ids))
        elif(classes == 'impostor'):
            q = q.filter(not_(File.client_id.in_(client_ids)))
    
    q = q.order_by(File.client_id, File.session, File.shot)
    
    # To remove duplicates
    def removeDup(seq):
      seen = set()
      seen_add = seen.add
      return [ x for x in seq if x not in seen and not seen_add(x)]
      
    return removeDup(list(q)) 
