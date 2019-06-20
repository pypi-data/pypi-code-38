#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Fri May 11 17:20:46 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module provides the Database interface allowing the user to query the
GBU database in the most obvious ways.
"""

from .models import *
from .driver import Interface

SQLITE_FILE = Interface().files()[0]

import os
import six

import bob.db.base


class Database(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension='.jpg'):
    # call base class constructor
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)

    # define some values that we will support
    self.m_groups = ('world', 'dev')  # GBU does not provide an eval set
    # Will be queried by the 'subworld' parameters
    self.m_sub_worlds = Subworld.subworld_choices
    self.m_purposes = Protocol.purpose_choices
    self.m_protocols = Protocol.protocol_choices
    # The type of protocols: The default GBU or one with multiple files per
    # model
    self.m_protocol_types = ('gbu', 'multi')

  def groups(self, protocol=None):
    """Returns a list of groups for the given protocol

    Keyword Parameters:

    protocol
      One or several of the GBU protocols ('Good', 'Bad', 'Ugly'), only valid if group is 'dev'.

    Returns: a list of groups
    """
    return self.m_groups

  def clients(self, groups=None, subworld=None, protocol=None):
    """Returns a list of clients for the specific query by the user.

    Keyword Parameters:

    groups
     One or several groups to which the models belong ('world', 'dev').

    subworld
      One or several training sets ('x1', 'x2', 'x4', 'x8'), only valid if group is 'world'.

    protocol
      One or several of the GBU protocols ('Good', 'Bad', 'Ugly'), only valid if group is 'dev'.

    Returns: A list containing all the Client objects which have the desired properties.
    """
    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    subworld = self.check_parameters_for_validity(
        subworld, "sub-world", self.m_sub_worlds)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.m_protocols)

    retval = []
    # List of the clients
    if 'world' in groups:
      query = self.query(Client).join(File).join((Subworld, File.subworlds))
      if subworld:
        query = query.filter(Subworld.name.in_(subworld))
      retval.extend([client for client in query])

    if 'dev' in groups:
      query = self.query(Client).join(File).join(
          (Protocol, File.protocols)).filter(Protocol.purpose == 'enroll')
      if protocol:
        query = query.filter(Protocol.name.in_(protocol))
      retval.extend([client for client in query])

    return retval

  def client_ids(self, groups=None, subworld=None, protocol=None):
    """Returns a list of client ids for the specific query by the user.

    Keyword Parameters:

    groups
     One or several groups to which the models belong ('world', 'dev').

    subworld
      One or several training sets ('x1', 'x2', 'x4', 'x8'), only valid if group is 'world'.

    protocol
      One or several of the GBU protocols ('Good', 'Bad', 'Ugly'), only valid if group is 'dev'.

    Returns: A list containing the ids of all clients which have the desired properties.
    """
    self.assert_validity()

    return [client.id for client in self.clients(groups, subworld, protocol)]

  def models(self, groups=None, subworld=None, protocol=None, protocol_type='gbu'):
    """Returns a list of models for the specific query by the user.
    The returned type of model depends on the protocol_type:

    * 'gbu': A list containing File objects (there is one model per file)
    * 'multi': A list containing Client objects (there is one model per client)

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev').

    subworld
      One or several training sets ('x1', 'x2', 'x4', 'x8'), only valid if group is 'world'.

    protocol
      One or several of the GBU protocols ('Good', 'Bad', 'Ugly'), only valid if group is 'dev'.

    protocol_type
      One protocol type from ('gbu', 'multi')

    Returns: A list containing all the models belonging to the given group.
    """
    protocol_type = self.check_parameter_for_validity(
        protocol_type, "types", self.m_protocol_types)

    if protocol_type == 'multi':
      # clients and models are the same
      return self.clients(groups, subworld, protocol)

    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    subworld = self.check_parameters_for_validity(
        subworld, "sub-world", self.m_sub_worlds)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.m_protocols)

    retval = []
    # query the files and extract their ids
    if 'world' in groups:
      query = self.query(File).join((Subworld, File.subworlds))
      if subworld:
        query = query.filter(Subworld.name.in_(subworld))
      retval.extend([file for file in query])

    if 'dev' in groups:
      query = self.query(File).join((Protocol, File.protocols)
                                    ).filter(Protocol.purpose == 'enroll')
      if protocol:
        query = query.filter(Protocol.name.in_(protocol))
      retval.extend([file for file in query])

    return retval

  def model_ids(self, groups=None, subworld=None, protocol=None, protocol_type='gbu'):
    """Returns a list of model ids for the specific query by the user.
    The returned list depends on the protocol_type:

    * 'gbu': A list containing file id's (there is one model per file)
    * 'multi': A list containing client id's (there is one model per client)

    .. note:: for the 'world' group, model ids are ALWAYS client ids

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev').

    subworld
      One or several training sets ('x1', 'x2', 'x4', 'x8'), only valid if group is 'world'.

    protocol
      One or several of the GBU protocols ('Good', 'Bad', 'Ugly'), only valid if group is 'dev'.

    protocol_type
      One protocol type from ('gbu', 'multi')

    Returns: A list containing all the model id's belonging to the given group.
    """
    protocol_type = self.check_parameter_for_validity(
        protocol_type, "types", self.m_protocol_types)

    if protocol_type == 'multi':
      # clients and models are the same
      return self.client_ids(groups, subworld, protocol)

    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    subworld = self.check_parameters_for_validity(
        subworld, "sub-world", self.m_sub_worlds)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.m_protocols)

    retval = []
    # for world group, we always have CLIENT IDS
    if 'world' in groups:
      query = self.query(Client).join(File).join((Subworld, File.subworlds))
      if subworld:
        query = query.filter(Subworld.name.in_(subworld))
      retval.extend([client.id for client in query])

    if 'dev' in groups:
      query = self.query(File).join((Protocol, File.protocols)
                                    ).filter(Protocol.purpose == 'enroll')
      if protocol:
        query = query.filter(Protocol.name.in_(protocol))
      retval.extend([file.id for file in query])

    return retval

  def get_client_id_from_file_id(self, file_id, **kwargs):
    """Returns the client id (real client id) attached to the given file id

    Keyword Parameters:

    file_id
      The file id to consider

    Returns: The client_id attached to the given file_id
    """
    self.assert_validity()

    query = self.query(File).filter(File.id == file_id)

    assert query.count() == 1
    return query.first().client_id

  def get_client_id_from_model_id(self, model_id, group='dev', protocol_type='gbu', **kwargs):
    """Returns the client id attached to the given model id.
    Dependent on the protocol type and the group, it is expected that

    * model_id is a file id, when protocol type is 'gbu'
    * model_id is a client id, when protocol type is 'multi' **or group is 'world'**

    Keyword Parameters:

    model_id
      The model id to consider

    group
      The group to which the model belong, might be 'world' or 'dev'.

    protocol_type
      One protocol type from ('gbu', 'multi')


    Returns: The client_id attached to the given model_id
    """

    protocol_type = self.check_parameter_for_validity(
        protocol_type, "protocol type", self.m_protocol_types)
    group = self.check_parameter_for_validity(group, "group", self.m_groups)

    if protocol_type == 'multi' or group == 'world':
      # client and model ids are identical
      return model_id
    else:
      return self.get_client_id_from_file_id(model_id)

  def objects(self, groups=None, subworld=None, protocol=None, purposes=None, model_ids=None, protocol_type='gbu'):
    """Using the specified restrictions, this function returns a list of File objects.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev').

    subworld
      One or several training sets ('x1', 'x2', 'x4', 'x8'), only valid if group is 'world'.

    protocol
      One or several of the GBU protocols ('Good', 'Bad', 'Ugly'), only valid if group is 'dev'.

    purposes
      One or several groups for which objects should be retrieved ('enroll', 'probe'),
      only valid when the group is 'dev'·

    model_ids
      If given (as a list of model id's or a single one), only the objects
      belonging to the specified model id is returned.
      The content of the model id is dependent on the protocol type:

      * model id is a file id, when protocol type is 'gbu'
      * model id is a client id, when protocol type is 'multi', **or when group is 'world'**

    protocol_type
      One protocol type from ('gbu', 'multi'), only required when model_ids are specified

    """

    def filter_model(query, protocol_type, model_ids):
      if model_ids and len(model_ids):
        if protocol_type == 'gbu':
          # for GBU protocol type, model id's are file id's
          query = query.filter(File.id.in_(model_ids))
        else:
          # for multi protocol type, model id's are client id's
          query = query.filter(File.client_id.in_(model_ids))
      return query

    # check that every parameter is as expected
    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    subworld = self.check_parameters_for_validity(
        subworld, "sub-world", self.m_sub_worlds)
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.m_protocols)
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.m_purposes)
    protocol_type = self.check_parameter_for_validity(
        protocol_type, 'protocol type', self.m_protocol_types)

    if isinstance(model_ids, six.string_types):
      model_ids = (model_ids,)
    # check that the model ids are in the actual set of model ids (for the
    # type of protocol that we are currently using)
    model_ids = self.check_parameters_for_validity(model_ids, 'model id', self.model_ids(
        groups=groups, subworld=subworld, protocol=protocol, protocol_type=protocol_type), [])

    retval = []

    if 'world' in groups:
      query = self.query(File).join((Subworld, File.subworlds))
      if subworld:
        query = query.filter(Subworld.name.in_(subworld))
      # here, we always filter by client ids (which is done by taking the
      # 'multi' protocol)
      query = filter_model(query, 'multi', model_ids)
      retval.extend([file for file in query])

    if 'dev' in groups:
      if 'enroll' in purposes:
        query = self.query(File).join((Protocol, File.protocols)).filter(
            Protocol.purpose == 'enroll')
        if protocol:
          query = query.filter(Protocol.name.in_(protocol))
        # filter model ids only when only the enroll objects are requested
        if model_ids:
          query = filter_model(query, protocol_type, model_ids)
        retval.extend([file for file in query])

      if 'probe' in purposes:
        query = self.query(File).join(
            (Protocol, File.protocols)).filter(Protocol.purpose == 'probe')
        if protocol:
          query = query.filter(Protocol.name.in_(protocol))
        retval.extend([file for file in query])

    return retval

  def annotations(self, file):
    """Returns the annotations for the given ``File`` object as a dictionary {'reye':(y,x), 'leye':(y,x)}."""
    self.assert_validity()

    # return the annotations as returned by the call function of the
    # Annotation object
    return file.annotation()
