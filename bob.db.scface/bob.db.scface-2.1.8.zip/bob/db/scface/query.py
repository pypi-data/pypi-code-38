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
SCFace database in the most obvious ways.
"""

from .models import *
from .driver import Interface

import bob.db.base

SQLITE_FILE = Interface().files()[0]


class Database(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension='.jpg'):
    # call base class constructors to open a session to the database
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)

  def groups(self, protocol=None):
    """Returns the names of all registered groups"""

    # Same as Client.group_choices for this database
    return ProtocolPurpose.group_choices

  def genders(self):
    """Returns the list of genders: 'm' for male and 'f' for female"""

    return Client.gender_choices

  def subworld_names(self):
    """Returns all registered subworld names"""

    l = self.subworlds()
    retval = [str(k.name) for k in l]
    return retval

  def subworlds(self):
    """Returns the list of subworlds"""

    return list(self.query(Subworld))

  def has_subworld(self, name):
    """Tells if a certain subworld is available"""

    return self.query(Subworld).filter(Subworld.name == name).count() != 0

  def clients(self, protocol=None, groups=None, subworld=None, gender=None, birthyear=None):
    """Returns a set of Clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      The groups to which the clients belong ('dev', 'eval', 'world')

    subworld
      Specify a split of the world data ("onethird", "twothirds", "")
      In order to be considered, "world" should be in groups and only one
      split should be specified.

    gender
      The genders to which the clients belong ('f', 'm')

    birthyear
      The birth year of the clients (in the range [1900,2050])

    Returns: A list containing all the clients which have the given
    properties.
    """

    protocol = self.check_parameters_for_validity(
        protocol, 'protocol', self.protocol_names())
    groups = self.check_parameters_for_validity(groups, 'group', self.groups())
    subworld = self.check_parameters_for_validity(
        subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(
        gender, "gender", self.genders(), [])
    birthyear = self.check_parameters_for_validity(
        birthyear, 'birthyear', list(range(1900, 2050)), [])

    retval = []
    # List of the clients
    if "world" in groups:
      q = self.query(Client).filter(Client.sgroup == 'world')
      if subworld:
        q = q.join((Subworld, Client.subworld)).filter(
            Subworld.name.in_(subworld))
      if gender:
        q = q.filter(Client.gender.in_(gender))
      if birthyear:
        q = q.filter(Client.birthyear.in_(birthyear))
      q = q.order_by(Client.id)
      retval += list(q)
    if 'dev' in groups or 'eval' in groups:
      q = self.query(Client).filter(
          and_(Client.sgroup != 'world', Client.sgroup.in_(groups)))
      if gender:
        q = q.filter(Client.gender.in_(gender))
      if birthyear:
        q = q.filter(Client.birthyear.in_(birthyear))
      q = q.order_by(Client.id)
      retval += list(q)
    return retval

  def tclients(self, protocol=None, groups=None):
    """Returns a set of T-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      Ignored.

    Returns: A list containing all the clients belonging to the given group.
    """

    # T-Norm clients are the ones from the onethird world subset
    return self.clients(protocol, 'world', 'onethird')

  def zclients(self, protocol=None, groups=None):
    """Returns a set of Z-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      The groups to which the clients belong ('dev', 'eval', 'world')

    Returns: A list containing all the models belonging to the given group.
    """

    # Z-Norm clients are the ones from the onethird world subset
    return self.clients(protocol, 'world', 'onethird')

  def models(self, protocol=None, groups=None):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    Returns: A list containing all the models belonging to the given group.
    """

    return self.clients(protocol, groups)

  def model_ids(self, protocol=None, groups=None):
    """Returns a set of models ids for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    Returns: A list containing the ids of all models belonging to the given group.
    """

    return [client.id for client in self.clients(protocol, groups)]

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    self.assert_validity()
    return self.query(Client).filter(Client.id == id).count() != 0

  def client(self, id):
    """Returns the Client object in the database given a certain id. Raises
    an error if that does not exist."""

    self.assert_validity()
    return self.query(Client).filter(Client.id == id).one()

  def tmodels(self, protocol=None, groups=None):
    """Returns a set of T-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      Ignored.

    Returns: A list containing all the T-Norm models.
    """

    return self.tclients(protocol, groups)

  def tmodel_ids(self, protocol=None, groups=None):
    """Returns a set of T-Norm model ids for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      Ignored.

    Returns: A list containing the ids of all T-Norm models.
    """
    return [client.id for client in self.tclients(protocol, groups)]

  def get_client_id_from_model_id(self, model_id, **kwargs):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model_id to consider

    Returns: The client_id attached to the given model_id
    """
    return model_id

  def objects(self, protocol=None, purposes=None, model_ids=None, groups=None,
              classes=None, subworld=None, distances=None):
    """Returns a set of Files for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the SCFace protocols ('combined', 'close', 'medium', 'far')

    purposes
      The purposes required to be retrieved ('enroll', 'probe', 'world') or a tuple
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

    subworld
      Specify a split of the world data ("onethird", "twothirds", "")
      In order to be considered, "world" should be in groups and only one
      split should be specified.

    distances
      Specify the subject-camera distance as an integral value.
      Possible values: (3: close, 2:medium, 1:far)

    Returns: A list of Files with the given properties
    """

    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    classes = self.check_parameters_for_validity(
        classes, "class", ('client', 'impostor'))
    subworld = self.check_parameters_for_validity(
        subworld, "subworld", self.subworld_names(), [])
    distances = self.check_parameters_for_validity(
        distances, "distance", (0, 1, 2, 3))

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids, collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    if 'world' in groups:
      q = self.query(File).join(Client).join(
          (ProtocolPurpose, File.protocol_purposes)).join(Protocol)
      if subworld:
        q = q.join((Subworld, Client.subworld)).filter(
            Subworld.name.in_(subworld))
      q = q.filter(and_(Protocol.name.in_(
          protocol), ProtocolPurpose.sgroup == 'world', File.distance.in_(distances)))
      if model_ids:
        q = q.filter(Client.id.in_(model_ids))
      q = q.order_by(File.client_id, File.camera, File.distance, File.id)
      retval += list(q)

    if ('dev' in groups or 'eval' in groups):
      if('enroll' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
            filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                groups), ProtocolPurpose.purpose == 'enroll'))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id, File.camera, File.distance, File.id)
        retval += list(q)

      if('probe' in purposes):
        if('client' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe', File.distance.in_(distances)))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.camera, File.distance, File.id)
          retval += list(q)

        if('impostor' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe', File.distance.in_(distances)))
          if len(model_ids) == 1:
            q = q.filter(not_(File.client_id.in_(model_ids)))
          q = q.order_by(File.client_id, File.camera, File.distance, File.id)
          retval += list(q)

    return list(set(retval))  # To remove duplicates

  def tobjects(self, protocol=None, model_ids=None, groups=None):
    """Returns a set of Files for enrolling T-norm models for score
       normalization.

    Keyword Parameters:

    protocol
      One of the SCFace protocols ('combined', 'close', 'medium', 'far')

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.

    Returns: A set of Files with the given properties
    """

    # ZT-Norm cohort is 'onethird'
    subworld = ('onethird',)
    # WARNING: Restrict to frontal camera (enroll T-Norm models)
    validcam = ('frontal',)

    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids, collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
        join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld)).\
        filter(and_(Protocol.name.in_(protocol),
                    ProtocolPurpose.sgroup == 'world', File.camera.in_(validcam)))
    if model_ids:
      q = q.filter(Client.id.in_(model_ids))
    q = q.order_by(File.client_id, File.camera, File.distance, File.id)
    retval += list(q)

    return retval

  def zobjects(self, protocol=None, model_ids=None, groups=None, distances=None):
    """Returns a set of Files to perform Z-norm score normalization.

    Keyword Parameters:

    protocol
      One of the SCFace protocols ('combined', 'close', 'medium', 'far')

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.

    distances
      Specify the subject-camera distance as an integral value.
      Possible values: (3: close, 2:medium, 1:far)

    Returns: A set of Files
    """

    # ZT-Norm cohort is 'onethird'
    subworld = ('onethird',)
    # WARNING: Restrict to non-frontal camera (enroll T-Norm models)
    validcam = ('cam1', 'cam2', 'cam3', 'cam4', 'cam5')

    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())
    distances = self.check_parameters_for_validity(
        distances, "distance", (1, 2, 3))

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids, collections.Iterable)):
      model_ids = (model_ids,)

    retval = []
    q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
        join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld)).\
        filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup ==
                    'world', File.camera.in_(validcam), File.distance.in_(distances)))
    if model_ids:
      q = q.filter(Client.id.in_(model_ids))
    q = q.order_by(File.client_id, File.camera, File.distance, File.id)
    retval += list(q)

    return retval

  def annotations(self, file):
    """Returns the annotations for the image with the given file id.

    Keyword Parameters:

    file
      The ``File`` object to retrieve the annotations for.

    Returns: the eye annotations as a dictionary {'reye':(y,x), 'leye':(y,x), 'mouth':(y,x), 'nose':(y,x)}.
    """

    self.assert_validity()
    # return the annotations as returned by the call function of the
    # Annotation object
    return file.annotation()

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

  def t_model_ids(self, protocol, groups='dev', **kwargs):
    """Returns the list of model ids used for T-Norm of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the :py:meth:`tmodel_ids` function."""
    return self.uniquify(self.tmodel_ids(protocol=protocol, groups=groups, **kwargs))

  def t_enroll_files(self, protocol, model_id, groups='dev', **kwargs):
    """Returns the list of T-Norm model enrollment File objects from the given model id of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the :py:meth:`tobjects` function."""
    return self.uniquify(self.tobjects(protocol=protocol, groups=groups, model_ids=(model_id,), **kwargs))

  def z_probe_files(self, protocol, groups='dev', **kwargs):
    """Returns the list of Z-Norm probe File objects to probe the model with the given model id of the given protocol for the given group that satisfy your query.
    For possible keyword arguments, please check the :py:meth:`zobjects` function."""
    return self.uniquify(self.zobjects(protocol=protocol, groups=groups, **kwargs))
