#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This module provides the Dataset interface allowing the user to query the
KBOC16 database in the most obvious ways.
"""

import six
from .models import *
from .driver import Interface

import bob.db.base

SQLITE_FILE = Interface().files()[0]


class Database(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension=db_file_extension):
    # call base class constructor
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)

  def __group_replace_eval_by_genuine__(self, l):
    """Replace 'eval' by 'Genuine' and returns the new list"""
    if not l:
      return l
    elif isinstance(l, six.string_types):
      return self.__group_replace_eval_by_genuine__((l,))
    l2 = []
    for val in l:
      if (val == 'eval'):
        l2.append('Genuine')
      elif (val in Client.type_choices):
        l2.append(val)
    return tuple(set(l2))

  def groups(self, protocol=None):
    """Returns the names of all registered groups"""

    return ProtocolPurpose.group_choices

  def client_groups(self):
    """Returns the names of the groups. This is specific to this database which
    does not have separate training, development and evaluation sets."""

    return ProtocolPurpose.group_choices

  def clients(self, protocol=None, groups='eval'):
    """Returns a list of :py:class:`.Client` for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups (types) to which the clients belong either from ('Genuine', 'Impostor')
      Note that 'eval' is an alias for 'Genuine'.
      If no groups are specified, then both clients are impostors are listed.

    Returns: A list containing all the clients which have the given properties.
    """

    """groups = self.__group_replace_eval_by_genuine__(groups)
    groups = self.check_parameters_for_validity(groups, "group", self.client_groups())"""
    # List of the clients
    #q = self.query(Client)
    if (protocol):
      q = self.query(Client).join(File).join((ProtocolPurpose, File.protocolPurposes)).join(
          Protocol).filter(and_(Protocol.name.in_((protocol,)), ProtocolPurpose.sgroup.in_((groups,))))
    else:
      q = self.query(Client)
    """if groups:
      q = q.filter(Client.sgroup.in_(groups))"""
    q = q.order_by(Client.id)
    return list(q)

  def models(self, protocol=None, groups='eval'):
    """Returns a list of :py:class:`.Client` for the specific query by the user.
       Models correspond to Clients for this database (At most one model per identity).

    Keyword Parameters:

    protocol
      'A' or 'D'.

    groups
      The groups to which the subjects attached to the models belong ('Genuine')
      Note that 'dev', 'eval' and 'world' are alias for 'Genuine'.

    Returns: A list containing all the models (model <-> client in AVTSKeystroke) belonging
             to the given group.
    """

    #groups = self.__group_replace_eval_by_genuine__(groups)
    #groups = self.check_parameters_for_validity(groups, "group", ('Genuine',))

    # List of the clients
    #q = self.query(Client)
    if (protocol):
      q = self.query(Client).join(File).join((ProtocolPurpose, File.protocolPurposes)).join(
          Protocol).filter(and_(Protocol.name.in_((protocol,)), ProtocolPurpose.sgroup.in_((groups,))))
    else:
      q = self.query(Client)
    """if groups:
      q = q.filter(Client.stype.in_(groups))
    else:
      q = q.filter(Client.stype.in_(['Genuine']))"""
    q = q.order_by(Client.id)
    return list(q)

  def model_ids(self, protocol=None, groups=None):
    """Returns a list of model ids for the specific query by the user.
       Models correspond to Clients for the XM2VTS database (At most one model per identity).

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')
      Note that 'dev', 'eval' and 'world' are alias for 'client'.
      If no groups are specified, then both clients are impostors are listed.

    Returns: A list containing all the model ids (model <-> client in XM2VTS) belonging
             to the given group.
    """

    return [client.id for client in self.models(protocol, groups)]

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    return self.query(Client).filter(Client.id == id).count() != 0

  def client(self, id):
    """Returns the client object in the database given a certain id. Raises
    an error if that does not exist."""

    return self.query(Client).filter(Client.id == id).one()

  def objects(self, protocol=None, purposes=None, model_ids=None, groups=None,
              classes=None):
    """Returns a list of :py:class:`.File` for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the KBOC16 protocols ('A').

    purposes
      The purposes required to be retrieved ('enrol', 'probe') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id). The model ids are string.  If 'None' is given (this is
      the default), no filter over the model_ids is performed.

    groups
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor')
      or a tuple with several of them. If 'None' is given (this is the
      default), it is considered the same as a tuple with all possible values.

    Returns: A list of :py:class:`.File` objects.
    """

    #groups = self.__group_replace_alias_clients__(groups)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    classes = self.check_parameters_for_validity(
        classes, "class", ('client', 'impostor'))

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids, collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []

    if ('eval' in groups):
      if('enrol' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
            filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                groups), ProtocolPurpose.purpose == 'enrol'))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id, File.session_id, File.shot_id)
        retval += list(q)

      if('probe' in purposes):
        if('client' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe'))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.session_id, File.shot_id)
          retval += list(q)

        if('impostor' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe'))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.session_id, File.shot_id)
          retval += list(q)

    return list(set(retval))  # To remove duplicates

  def protocol_names(self):
    """Returns all registered protocol names"""

    l = self.protocols()
    retval = [str(k.name) for k in l]
    return retval

  def protocols(self):
    """Returns all registered protocols"""

    return list(self.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""

    return self.query(Protocol).filter(Protocol.name == name).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    return self.query(Protocol).filter(Protocol.name == name).one()

  def protocol_purposes(self):
    """Returns all registered protocol purposes"""

    return list(self.query(ProtocolPurpose))

  def purposes(self):
    """Returns the list of allowed purposes"""

    return ProtocolPurpose.purpose_choices
