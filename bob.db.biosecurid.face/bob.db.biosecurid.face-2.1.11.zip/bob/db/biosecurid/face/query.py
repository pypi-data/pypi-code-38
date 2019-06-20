#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This module provides the Dataset interface allowing the user to query the
BiosecurID database in the most obvious ways.
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

  def __init__(self, original_directory=None, original_extension='.bmp'):
    # call base class constructor
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)

  def __group_replace_alias__(self, l):
    """Replace 'dev' by 'clientDev' and 'eval' by 'clientEval' in a list of groups, and
       returns the new list"""
    if not l:
      return l
    elif isinstance(l, six.string_types):
      return self.__group_replace_alias__((l,))
    l2 = []
    for val in l:
      if(val == 'dev'):
        l2.append('clientDev')
      if(val == 'eval'):
        l2.append('clientEval')
    return tuple(set(l2))

  def __group_replace_alias_clients__(self, l):
    """Replace 'dev' by 'clientDev' and 'eval' by 'clientEval' in a list of groups, and
       returns the new list"""
    if not l:
      return l
    elif isinstance(l, six.string_types):
      return self.__group_replace_alias_clients__((l,))
    l2 = []
    for val in l:
      if(val == 'dev' or val == 'eval'):
        if(val == 'dev'):
          l2.extend(['clientDev', 'impostorDev'])
        if(val == 'eval'):
          l2.extend(['clientEval', 'impostorEval'])
      else:
        l2.append(val)
    return tuple(set(l2))

  def groups(self, protocol=None):
    """Returns the names of all registered groups"""

    return ProtocolPurpose.group_choices

  def client_groups(self):
    """Returns the names of the XM2VTS groups. This is specific to this database which
    does not have separate training, development and evaluation sets."""

    return Client.group_choices

  def clients(self, protocol=None, groups=None):
    """Returns a list of :py:class:`.Client` for the specific query by the user.

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the clients belong either from ('dev', 'eval', 'world')
      or the specific XM2VTS ones from ('client', 'impostorDev', 'impostorEval')
      Note that 'dev', 'eval' and 'world' are alias for 'client'.
      If no groups are specified, then both clients are impostors are listed.

    Returns: A list containing all the clients which have the given properties.
    """

    groups = self.__group_replace_alias_clients__(groups)
    groups = self.check_parameters_for_validity(
        groups, "group", self.client_groups())
    # List of the clients
    q = self.query(Client)
    if groups:
      q = q.filter(Client.sgroup.in_(groups))
    q = q.order_by(Client.id)
    return list(q)

  def models(self, protocol=None, groups=None):
    """Returns a list of :py:class:`.Client` for the specific query by the user.
       Models correspond to Clients for the XM2VTS database (At most one model per identity).

    Keyword Parameters:

    protocol
      Ignored.

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')
      Note that 'dev', 'eval' and 'world' are alias for 'client'.
      If no groups are specified, then both clients are impostors are listed.

    Returns: A list containing all the models (model <-> client in BiosecurID) belonging
             to the given group.
    """

    # List of the clients
    q = self.query(Client)
    if groups:
      q = q.filter(Client.sgroup.in_(self.__group_replace_alias__(groups)))
    else:
      q = q.filter(Client.sgroup.in_(['clientDev', 'clientEval']))
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
      One of the Biosecurid protocols ('A').

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

    if 'world' in groups:
      q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
          filter(Client.sgroup == 'world').\
          filter(and_(Protocol.name.in_(protocol),
                      ProtocolPurpose.sgroup == 'world'))
      if model_ids:
        q = q.filter(Client.id.in_(model_ids))
      q = q.order_by(File.client_id, File.session_id, File.shot_id)
      retval += list(q)

    if ('dev' in groups or 'eval' in groups):
      if('enrol' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
            filter(Client.sgroup.in_(['clientDev', 'clientEval'])).\
            filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                groups), ProtocolPurpose.purpose == 'enrol'))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id, File.session_id, File.shot_id)
        retval += list(q)

      if('probe' in purposes):
        if('client' in classes):
          ltmp = []
          if('dev' in groups):
            ltmp.append('clientDev')
          if('eval' in groups):
            ltmp.append('clientEval')
          clientGroups = tuple(ltmp)
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(Client.sgroup.in_(clientGroups)).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe'))
          # print(model_ids)
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.session_id, File.shot_id)
          retval += list(q)

        # Exhaustive tests using the impostor{Dev,Eval} sets -> no need to
        # check for model_ids
        if('impostor' in classes):
          ltmp = []
          if('dev' in groups):
            ltmp.append('impostorDev')
          if('eval' in groups):
            ltmp.append('impostorEval')
          impostorGroups = tuple(ltmp)
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(Client.sgroup.in_(ltmp)).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe'))
          q = q.order_by(File.client_id, File.session_id, File.shot_id)
          retval += list(q)

          # Needs to add 'client-impostor' samples
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(Client.sgroup == 'client').\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe'))
          if(len(model_ids) == 1):
            q = q.filter(not_(Client.id.in_(model_ids)))
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
