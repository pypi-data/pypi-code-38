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
MOBIO database in the most obvious ways.
"""

import six
from .models import *
from .driver import Interface
from sqlalchemy import and_, not_

import bob.db.base

SQLITE_FILE = Interface().files()[0]


class Database(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension=None, annotation_directory=None, annotation_extension='.pos'):
    # call base class constructors to open a session to the database
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)

    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension

  def groups(self, protocol=None):
    """Returns the names of all registered groups"""

    return ProtocolPurpose.group_choices

  def genders(self):
    """Returns the list of genders"""

    return Client.gender_choices

  def subworld_names(self):
    """Returns all registered subworld names"""

    self.assert_validity()
    l = self.subworlds()
    retval = [str(k.name) for k in l]
    return retval

  def subworlds(self):
    """Returns the list of subworlds"""

    return list(self.query(Subworld))

  def has_subworld(self, name):
    """Tells if a certain subworld is available"""

    self.assert_validity()
    return self.query(Subworld).filter(Subworld.name == name).count() != 0

  def _replace_protocol_alias(self, protocol):
    if protocol == 'male':
      return 'mobile0-male'
    elif protocol == 'female':
      return 'mobile0-female'
    else:
      return protocol

  def _replace_protocols_alias(self, protocol):
    # print(protocol)
    if protocol:
      from six import string_types
      if isinstance(protocol, string_types):
        # print([self._replace_protocol_alias(protocol)])
        return [self._replace_protocol_alias(protocol)]
      else:
        # print(list(set(self._replace_protocol_alias(k) for k in protocols)))
        return list(set(self._replace_protocol_alias(k) for k in protocols))
    else:
      return None

  def clients(self, protocol=None, groups=None, subworld=None, gender=None):
    """Returns a list of Clients for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    groups
      The groups to which the clients belong ('dev', 'eval', 'world')
      Please note that world data are protocol/gender independent

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      In order to be considered, 'world' should be in groups and only one
      split should be specified.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the clients which have the given properties.
    """

    protocol = self._replace_protocols_alias(protocol)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names(), [])
    groups = self.check_parameters_for_validity(
        groups, "group", self.groups(), self.groups())
    subworld = self.check_parameters_for_validity(
        subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(
        gender, "gender", self.genders(), [])

    # List of the clients
    retval = []
    if 'world' in groups:
      q = self.query(Client).filter(Client.sgroup == 'world')
      if subworld:
        q = q.join((Subworld, Client.subworld)).filter(
            Subworld.name.in_(subworld))
      if gender:
        q = q.filter(Client.gender.in_(gender))
      q = q.order_by(Client.id)
      retval += list(q)

    dev_eval = []
    if 'dev' in groups:
      dev_eval.append('dev')
    if 'eval' in groups:
      dev_eval.append('eval')
    if dev_eval:
      protocol_gender = None
      if protocol:
        q = self.query(Protocol).filter(Protocol.name.in_(protocol)).one()
        protocol_gender = [q.gender]
      q = self.query(Client).filter(Client.sgroup.in_(dev_eval))
      if protocol_gender:
        q = q.filter(Client.gender.in_(protocol_gender))
      if gender:
        q = q.filter(Client.gender.in_(gender))
      q = q.order_by(Client.id)
      retval += list(q)

    return retval

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    return self.query(Client).filter(Client.id == id).count() != 0

  def client(self, id):
    """Returns the Client object in the database given a certain id. Raises
    an error if that does not exist."""

    return self.query(Client).filter(Client.id == id).one()

  def tclients(self, protocol=None, groups=None, subworld='onethird', gender=None):
    """Returns a set of T-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    groups
      Ignored.
      For the MOBIO database, this has no impact as the T-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the T-norm clients belonging to the given group.
    """

    return self.clients(protocol, 'world', subworld, gender)

  def zclients(self, protocol=None, groups=None, subworld='onethird', gender=None):
    """Returns a set of Z-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    groups
      Ignored.
      For the MOBIO database, this has no impact as the Z-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the Z-norm clients belonging to the given group.
    """

    return self.clients(protocol, 'world', subworld, gender)

  def models(self, protocol=None, groups=None, subworld=None, gender=None):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')
      Please note that world data are protocol/gender independent

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      In order to be considered, 'world' should be in groups and only one
      split should be specified.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the models belonging to the given group.
    """

    return self.clients(protocol, groups, subworld, gender)

  def model_ids(self, protocol=None, groups=None, subworld=None, gender=None):
    """Returns a set of models ids for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')
      Please note that world data are protocol/gender independent

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      In order to be considered, 'world' should be in groups and only one
      split should be specified.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing the ids of all models belonging to the given group.
    """

    return [client.id for client in self.clients(protocol, groups, subworld, gender)]

  def tmodels(self, protocol=None, groups=None, subworld='onethird', gender=None):
    """Returns a set of T-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    groups
      Ignored.
      For the MOBIO database, this has no impact as the T-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing all the T-norm models belonging to the given group.
    """

    protocol = self._replace_protocols_alias(protocol)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())
    subworld = self.check_parameters_for_validity(
        subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(
        gender, "gender", self.genders(), [])

    # List of the clients
    q = self.query(TModel).join(Client).join(
        Protocol).filter(Protocol.name.in_(protocol))
    if subworld:
      q = q.join((Subworld, Client.subworld)).filter(
          Subworld.name.in_(subworld))
    if gender:
      q = q.filter(Client.gender.in_(gender))
    q = q.order_by(TModel.id)
    return list(q)

  def tmodel_ids(self, protocol=None, groups=None, subworld='onethird', gender=None):
    """Returns a list of ids of T-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    groups
      Ignored.
      For the MOBIO database, this has no impact as the T-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    Returns: A list containing the ids of all T-norm models belonging to the given group.
    """
    return [tmodel.mid for tmodel in self.tmodels(protocol, groups, subworld, gender)]

  def get_client_id_from_model_id(self, model_id, **kwargs):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model_id to consider

    Returns: The client_id attached to the given model_id
    """
    return model_id

  def objects(self, protocol=None, purposes=None, model_ids=None,
              groups=None, classes=None, subworld=None, gender=None, device=None):
    """Returns a set of Files for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    purposes
      The purposes required to be retrieved ('enroll', 'probe') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor')
      or a tuple with several of them. If 'None' is given (this is the
      default), it is considered the same as a tuple with all possible values.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      In order to be considered, "world" should be in groups and only one
      split should be specified.

    gender
      The gender to consider ('male', 'female')

    device
      The device to consider ('laptop', 'mobile')

    Returns: A set of Files with the given properties.
    """

    protocol = self._replace_protocols_alias(protocol)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    classes = self.check_parameters_for_validity(
        classes, "class", ('client', 'impostor'))
    subworld = self.check_parameters_for_validity(
        subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(
        gender, "gender", self.genders(), [])
    device = self.check_parameters_for_validity(
        device, "device", File.device_choices, [])

    import collections
    if(model_ids is None):
      model_ids = ()
    elif not isinstance(model_ids, collections.Iterable):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    if 'world' in groups and 'train' in purposes:
      q = self.query(File).join(Client).filter(Client.sgroup == 'world').join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
          filter(and_(Protocol.name.in_(protocol),
                      ProtocolPurpose.sgroup == 'world'))
      if subworld:
        q = q.join((Subworld, File.subworld)).filter(
            Subworld.name.in_(subworld))
      if gender:
        q = q.filter(Client.gender.in_(gender))
      if device:
        q = q.filter(File.device.in_(device))
      if model_ids:
        q = q.filter(File.client_id.in_(model_ids))
      q = q.order_by(File.client_id, File.session_id,
                     File.speech_type, File.shot_id, File.device)
      retval += list(q)

    if ('dev' in groups or 'eval' in groups):
      if('enroll' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
            filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                groups), ProtocolPurpose.purpose == 'enroll'))
        if gender:
          q = q.filter(Client.gender.in_(gender))
        if device:
          q = q.filter(File.device.in_(device))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id, File.session_id,
                       File.speech_type, File.shot_id, File.device)
        retval += list(q)

      if('probe' in purposes):
        if('client' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe'))
          if gender:
            q = q.filter(Client.gender.in_(gender))
          if device:
            q = q.filter(File.device.in_(device))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.session_id,
                         File.speech_type, File.shot_id, File.device)
          retval += list(q)

        if('impostor' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(
                  groups), ProtocolPurpose.purpose == 'probe'))
          if gender:
            q = q.filter(Client.gender.in_(gender))
          if device:
            q = q.filter(File.device.in_(device))
          if len(model_ids) == 1:
            q = q.filter(not_(File.client_id.in_(model_ids)))
          q = q.order_by(File.client_id, File.session_id,
                         File.speech_type, File.shot_id, File.device)
          retval += list(q)

    return sorted(list(set(retval)), key=lambda x: x.id)  # To remove duplicates

  def tobjects(self, protocol=None, model_ids=None, groups=None, subworld='onethird', gender=None, speech_type=None, device=None):
    """Returns a set of filenames for enrolling T-norm models for score
       normalization.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    model_ids
      Only retrieves the files for the provided list of model ids.
      If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.
      For the MOBIO database, this has no impact as the T-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    speech_type
      The speech type to consider ('p', 'l', 'r', 'f')

    device
      The device choice to consider ('mobile', 'laptop')

    Returns: A set of Files with the given properties.
    """

    protocol = self._replace_protocols_alias(protocol)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())
    subworld = self.check_parameters_for_validity(
        subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(
        gender, "gender", self.genders(), [])

    if(model_ids is None):
      model_ids = ()
    elif isinstance(model_ids, six.string_types):
      model_ids = (model_ids,)

    # Now query the database
    q = self.query(File, Protocol).filter(
        Protocol.name.in_(protocol)).join(Client)
    if subworld:
      q = q.join((Subworld, File.subworld)).filter(Subworld.name.in_(subworld))
    q = q.join((TModel, File.tmodels)).filter(
        TModel.protocol_id == Protocol.id)
    if model_ids:
      q = q.filter(TModel.mid.in_(model_ids))
    if gender:
      q = q.filter(Client.gender.in_(gender))
    if speech_type:
      q = q.filter(File.speech_type.in_(speech_type))
    if device:
      q = q.filter(File.device.in_(device))
    q = q.order_by(File.client_id, File.session_id,
                   File.speech_type, File.shot_id, File.device)
    retval = [v[0] for v in q]
    return list(retval)

  def zobjects(self, protocol=None, model_ids=None, groups=None, subworld='onethird', gender=None, speech_type=['r', 'f'], device=['mobile']):
    """Returns a set of Files to perform Z-norm score normalization.

    Keyword Parameters:

    protocol
      One of the MOBIO protocols ('mobile0-male', 'mobile0-female', 'mobile1-male', 'mobile1-female', \
        'laptop1-male', 'laptop1-female', 'laptop_mobile1-male', 'laptop_mobile1-female')
      'male'and 'female' are aliases for 'mobile0-male' and 'mobile0-female', respectively.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.
      For the MOBIO database, this has no impact as the Z-Norm clients are coming from
      the 'world' set, and are hence the same for both the 'dev' and 'eval' sets.

    subworld
      Specify a split of the world data ('onethird', 'twothirds', 'twothirds-subsampled')
      Please note that 'onethird' is the default value.

    gender
      The gender to consider ('male', 'female')

    speech_type
      The speech type to consider ('p', 'l', 'r', 'f')

    device
      The device choice to consider ('mobile', 'laptop')

    Returns: A set of Files with the given properties.
    """

    protocol = self._replace_protocols_alias(protocol)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    subworld = self.check_parameters_for_validity(
        subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(
        gender, "gender", self.genders(), [])
    speech_type = self.check_parameters_for_validity(
        speech_type, "speech_type", File.speech_type_choices)
    device = self.check_parameters_for_validity(
        device, "device", File.device_choices)

    import collections
    if(model_ids is None):
      model_ids = ()
    elif not isinstance(model_ids, collections.Iterable):
      model_ids = (model_ids,)

    # Now query the database
    q = self.query(File).join(Client).filter(Client.sgroup == 'world').join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
        filter(and_(Protocol.name.in_(protocol),
                    ProtocolPurpose.sgroup == 'world'))
    if subworld:
      q = q.join((Subworld, File.subworld)).filter(Subworld.name.in_(subworld))
    if gender:
      q = q.filter(Client.gender.in_(gender))
    if speech_type:
      q = q.filter(File.speech_type.in_(speech_type))
    if device:
      q = q.filter(File.device.in_(device))
    if model_ids:
      q = q.filter(File.client_id.in_(model_ids))
    q = q.order_by(File.client_id, File.session_id,
                   File.speech_type, File.shot_id, File.device)
    return list(q)

  def annotations(self, file):
    """Reads the annotations for the given file id from file and returns them in a dictionary.

    If you don't have a copy of the annotation files, you can download them under http://www.idiap.ch/resource/biometric.

    Keyword parameters:

    file
      The ``File`` object for which the annotations should be read.

    Return value
      The annotations as a dictionary: {'reye':(re_y,re_x), 'leye':(le_y,le_x)}
    """
    if self.annotation_directory is None:
      return None

    self.assert_validity()
    annotation_file = file.make_path(
        self.annotation_directory, self.annotation_extension)

    # return the annotations as read from file
    return bob.db.base.read_annotation_file(annotation_file, 'eyecenter')

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

    return self.query(Protocol).filter(Protocol.name == self._replace_protocol_alias(name)).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    return self.query(Protocol).filter(Protocol.name == self._replace_protocol_alias(name)).one()

  def protocol_purposes(self):
    """Returns all registered protocol purposes"""

    return list(self.query(ProtocolPurpose))

  def purposes(self):
    """Returns the list of allowed purposes"""

    return ProtocolPurpose.purpose_choices
