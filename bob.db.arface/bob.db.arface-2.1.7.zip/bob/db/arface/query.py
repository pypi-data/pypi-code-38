#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Wed Jul  4 14:12:51 CEST 2012
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
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
AR face database.
"""

import os
import six
from .models import *
from .driver import Interface

import bob.db.base

SQLITE_FILE = Interface().files()[0]


class Database(bob.db.base.SQLiteDatabase):
  """The database class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension='.ppm'):
    # call base class constructor
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory,
                                   original_extension)

    # defines valid entries for various parameters
    self.m_groups = Client.group_choices
    self.m_purposes = File.purpose_choices
    self.m_genders = Client.gender_choices
    self.m_sessions = File.session_choices
    self.m_expressions = File.expression_choices
    self.m_illuminations = File.illumination_choices
    self.m_occlusions = File.occlusion_choices
    self.m_protocols = Protocol.protocol_choices

  def groups(self, protocol=None):
    """Returns the names of all registered groups"""

    return self.m_groups

  def clients(self, groups=None, genders=None, protocol=None):
    """Returns a list of Client objects for the specific query by the user.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev', 'eval').
      If not specified, all groups are returned.

    genders
      One of the genders ('m', 'w') of the clients.
      If not specified, clients of all genders are returned.

    protocol
      Ignored since clients are identical for all protocols.

    Returns: A list containing all the Client objects which have the desired properties.
    """

    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    genders = self.check_parameters_for_validity(
        genders, "group", self.m_genders)

    query = self.query(Client)\
                .filter(Client.sgroup.in_(groups))\
                .filter(Client.gender.in_(genders))

    return [client for client in query]

  def client_ids(self, groups=None, genders=None, protocol=None):
    """Returns a list of client ids for the specific query by the user.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev', 'eval').
      If not specified, all groups are returned.

    genders
      One of the genders ('m', 'w') of the clients.
      If not specified, clients of all genders are returned.

    protocol
      Ignored since clients are identical for all protocols.

    Returns: A list containing all the client ids which have the desired properties.
    """

    return [client.id for client in self.clients(groups, genders, protocol)]

  # model_ids() and client_ids() functions are identical
  model_ids = client_ids

  def get_client_id_from_file_id(self, file_id, **kwargs):
    """Returns the client_id (real client id) attached to the given file_id

    Keyword Parameters:

    file_id
      The file_id to consider

    Returns: The client_id attached to the given file_id
    """
    q = self.query(File)\
            .filter(File.id == file_id)

    assert q.count() == 1
    return q.first().client_id

  def get_client_id_from_model_id(self, model_id, **kwargs):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model id to consider

    Returns: The client_id attached to the given model_id
    """
    # client ids and model ids are identical...
    return model_id

  def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, sessions=None, expressions=None, illuminations=None, occlusions=None, genders=None):
    """Using the specified restrictions, this function returns a list of File objects.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev', 'eval').

    protocol
      One of the AR protocols ('all', 'expression', 'illumination', 'occlusion', 'occlusion_and_illumination').
      Note: this field is ignored for group 'world'.

    purposes
      One or several purposes for which files should be retrieved ('enroll', 'probe').
      Note: this field is ignored for group 'world'.

    model_ids
      If given (as a list of model id's or a single one), only the files belonging to the specified model id is returned.
      For 'probe' purposes, this field is ignored since probe files are identical for all models.

    sessions
      One or several sessions from ('first', 'second').
      If not specified, objects of all sessions are returned.

    expressions
      One or several expressions from ('neutral', 'smile', 'anger', 'scream').
      If not specified, objects with all expressions are returned.
      Ignored for purpose 'enroll'.

    illuminations
      One or several illuminations from ('front', 'left', 'right', 'all').
      If not specified, objects with all illuminations are returned.
      Ignored for purpose 'enroll'.

    occlusions
      One or several occlusions from ('none', 'sunglasses', 'scarf').
      If not specified, objects with all occlusions are returned.
      Ignored for purpose 'enroll'.

    genders
      One of the genders ('m', 'w') of the clients.
      If not specified, both genders are returned.

    """
    # check that every parameter is as expected
    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.m_purposes)
    sessions = self.check_parameters_for_validity(
        sessions, "session", self.m_sessions)
    expressions = self.check_parameters_for_validity(
        expressions, "expression", self.m_expressions)
    illuminations = self.check_parameters_for_validity(
        illuminations, "illumination", self.m_illuminations)
    occlusions = self.check_parameters_for_validity(
        occlusions, "occlusion", self.m_occlusions)
    genders = self.check_parameters_for_validity(
        genders, "gender", self.m_genders)

    # assure that the given model ids are in a tuple
    if isinstance(model_ids, six.string_types):
      model_ids = (model_ids,)

    def _filter_types(query):
      return query.filter(File.expression.in_(expressions))\
                  .filter(File.illumination.in_(illuminations))\
                  .filter(File.occlusion.in_(occlusions))\
                  .filter(File.session.in_(sessions))\
                  .filter(Client.gender.in_(genders))
      return query

    queries = []
    probe_queries = []

    if 'world' in groups:
      queries.append(
          _filter_types(
              self.query(File).join(Client)
              .filter(Client.sgroup == 'world')
          )
      )

    if 'dev' in groups or 'eval' in groups:
      protocol = self.check_parameter_for_validity(
          protocol, "protocol", self.m_protocols, 'all')

      t_groups = ('dev',) if not 'eval' in groups else (
          'eval',) if not 'dev' in groups else ('dev', 'eval')

      if 'enroll' in purposes:
        queries.append(
            self.query(File).join(Client)
                .filter(Client.sgroup.in_(t_groups))
                .filter(Client.gender.in_(genders))
                .filter(File.purpose == 'enroll')
        )

      if 'probe' in purposes:
        probe_queries.append(
            _filter_types(
                self.query(File).join(Client)
                .join((Protocol, and_(File.expression == Protocol.expression, File.illumination == Protocol.illumination, File.occlusion == Protocol.occlusion)))
                .filter(Client.sgroup.in_(t_groups))
                .filter(File.purpose == 'probe')
                .filter(Protocol.name == protocol)
            )
        )

    # we have collected all queries, now filter the model ids, if desired
    retval = []

    for query in queries:
      # filter model ids
      if model_ids is not None:
        query = query.filter(Client.id.in_(model_ids))
      retval.extend([file for file in query])

    for query in probe_queries:
      # do not filter model ids
      retval.extend([file for file in query])

    return retval

  def annotations(self, file):
    """Returns the annotations for the image with the given file id.

    Keyword Parameters:

    file
      The `File` object to retrieve the annotations for.

    Returns: the eye annotations as a dictionary {'reye':(y,x), 'leye':(y,x)}.
    """

    self.assert_validity()
    # return the annotations as returned by the call function of the
    # Annotation object
    return file.annotation()
