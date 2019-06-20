#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This module provides the Dataset interface allowing the user to query the
Biosecure database in the most obvious ways.
"""

import os
from .models import *
from .driver import Interface

import bob.db.base

SQLITE_FILE = Interface().files()[0]

class Database(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory = None, original_extension = '.jpg'):
    # call base class constructors
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)

  def groups(self, protocol=None):
    """Returns the names of all registered groups"""

    return ProtocolPurpose.group_choices # Same as Client.group_choices for this database

  def clients(self, protocol=None, groups=None):
    """Returns a set of clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('ca0', 'caf', 'wc')

    groups
      The groups to which the clients belong ('dev', 'eval', 'world')

    Returns: A list containing all the clients which have the given properties.
    """

    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    # List of the clients
    q = self.query(Client).filter(Client.sgroup.in_(groups)).\
          order_by(Client.id)
    return list(q)

  def models(self, protocol=None, groups=None):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('ca0', 'caf', 'wc')

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    Returns: A list containing all the models belonging to the given group.
    """

    return self.clients(protocol, groups)

  def model_ids(self, protocol=None, groups=None):
    """Returns a list of model ids for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('ca0', 'caf', 'wc')

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    Returns: A list containing the ids of all models belonging to the given group.
    """

    return [client.id for client in self.clients(protocol, groups)]

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    return self.query(Client).filter(Client.id==id).count() != 0

  def client(self, id):
    """Returns the client object in the database given a certain id. Raises
    an error if that does not exist."""

    return self.query(Client).filter(Client.id==id).one()

  def get_client_id_from_model_id(self, model_id, **kwargs):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model_id to consider

    Returns: The client_id attached to the given model_id
    """
    return model_id

  def objects(self, protocol=None, purposes=None, model_ids=None, groups=None,
      classes=None):
    """Returns a set of filenames for the specific query by the user.
    WARNING: Files used as impostor access for several different models are
    only listed one and refer to only a single model

    Keyword Parameters:

    protocol
      One of the Biosecure protocols ('ca0', 'caf', 'wc').

    purposes
      The purposes required to be retrieved ('enroll', 'probe', 'train') or a tuple
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

    Returns: A list of files which have the given properties.
    """

    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    classes = self.check_parameters_for_validity(classes, "class", ('client', 'impostor'))

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids,collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    if 'world' in groups:
      q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol)
      q = q.filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup == 'world'))
      if model_ids:
        q = q.filter(Client.id.in_(model_ids))
      q = q.order_by(File.client_id, File.camera, File.session_id, File.shot_id)
      retval += list(q)

    if ('dev' in groups or 'eval' in groups):
      if('enroll' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'enroll'))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id, File.camera, File.session_id, File.shot_id)
        retval += list(q)

      if('probe' in purposes):
        if('client' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
                filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'probe'))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.camera, File.session_id, File.shot_id)
          retval += list(q)

        if('impostor' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
                filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'probe'))
          if len(model_ids) == 1:
            q = q.filter(not_(File.client_id.in_(model_ids)))
          q = q.order_by(File.client_id, File.camera, File.session_id, File.shot_id)
          retval += list(q)

    return list(set(retval)) # To remove duplicates

  def annotations(self, file):
    """Returns the annotations for the image with the given file id.

    Keyword Parameters:

    file
      The ``File`` object to retrieve the annotations for.

    Returns: the eye annotations as a dictionary {'reye':(y,x), 'leye':(y,x)}.
    """

    self.assert_validity()
    # return the annotations as returned by the call function of the Annotation object
    return file.annotation()


  def protocol_names(self):
    """Returns all registered protocol names"""

    return [str(p.name) for p in self.protocols()]

  def protocols(self):
    """Returns all registered protocols"""

    return list(self.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""

    return self.query(Protocol).filter(Protocol.name==name).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    return self.query(Protocol).filter(Protocol.name==name).one()

  def protocol_purposes(self):
    """Returns all registered protocol purposes"""

    return list(self.query(ProtocolPurpose))

  def purposes(self):
    """Returns the list of allowed purposes"""

    return ProtocolPurpose.purpose_choices


