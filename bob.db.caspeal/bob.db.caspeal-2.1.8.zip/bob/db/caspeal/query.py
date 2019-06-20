#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Mon Dec 10 14:29:51 CET 2012
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
CAS-PEAL database.
"""

import os
from bob.db.base import utils
from .models import *
from .driver import Interface

import bob.db.base

SQLITE_FILE = Interface().files()[0]


class Database(bob.db.base.SQLiteDatabase):
  """The database class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension='.tif'):
    # call base class constructor
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)

    # defines valid entries for various parameters
    self.m_groups = ('world', 'dev')  # no eval
    self.m_purposes = ('enroll', 'probe')
    self.m_genders = Client.gender_choices
    self.m_ages = Client.age_choices
    self.m_lightings = File.lighting_choices
    self.m_poses = File.pose_choices
    self.m_expressions = File.expression_choices
    self.m_accessories = File.accessory_choices
    self.m_distances = File.distance_choices
    self.m_sessions = File.session_choices
    self.m_backgrounds = File.background_choices
    self.m_protocols = Protocol.protocol_choices[2:]

  def groups(self, protocol=None):
    """Returns a list of groups for the given protocol

    Keyword Parameters:

    protocol
      Ignored since groups are identical for all protocols.

    Returns: a list of groups
    """
    return self.m_groups

  def clients(self, groups=None, genders=None, ages=None, protocol=None):
    """Returns a list of Client objects for the specific query by the user.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev').
      If not specified, all groups are returned.

    genders
      One or several of the genders ('F', 'M') of the clients.
      If not specified, clients of all genders are returned.

    ages
      One or several of the age ranges ('Y', 'M', 'O') of the clients.
      If not specified, clients of all age ranges are returned.

    protocol
      Ignored since clients are identical for all protocols.

    Returns: A list containing all the Client objects which have the desired properties.
    """

    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    genders = self.check_parameters_for_validity(
        genders, "gender", self.m_genders)
    ages = self.check_parameters_for_validity(ages, "age range", self.m_ages)

    query = self.query(Client)\
                .filter(Client.gender.in_(genders))\
                .filter(Client.age.in_(ages))

    if groups == ('world',):
      # sub-select only those clients who are in the training set
      query = query.join(File).filter(File.purpose == 'world')

    return [client for client in query]

  def client_ids(self, groups=None, genders=None, ages=None, protocol=None):
    """Returns a list of client ids for the specific query by the user.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev', 'eval').
      If not specified, all groups are returned.

    genders
      One of the genders ('m', 'w') of the clients.
      If not specified, clients of all genders are returned.

    ages
      One or several of the age ranges ('Y', 'M', 'O') of the clients.
      If not specified, clients of all age ranges are returned.

    protocol
      Ignored since clients are identical for all protocols.

    Returns: A list containing all the client ids which have the desired properties.
    """

    return [client.id for client in self.clients(groups, genders, ages, protocol)]

  # model_ids() and client_ids() functions are identical
  model_ids = client_ids

  def get_client_id_from_file_id(self, file_id, **kwargs):
    """Returns the client_id attached to the given file_id

    Keyword Parameters:

    file_id
      The file_id to consider

    Returns: The client_id attached to the given file_id
    """
    q = self.query(File)\
            .filter(File.id == file_id)

    assert q.count() == 1
    return q.first().client_id

  def get_client_id_from_model_id(self, model_id):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model id to consider

    Returns: The client_id attached to the given model_id
    """
    # client ids and model ids are identical...
    return model_id

  def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, genders=None, ages=None, lightings=None, poses=None, expressions=None, accessories=None, distances=None, sessions=None, backgrounds=None):
    """Using the specified restrictions, this function returns a list of File objects.

    Note that in rare cases, File objects with the same path, but different ID's might be returned.
    This is due to the fact that some images are in both the training list and in one of the gallery or probe lists.

    Note further that the training set consists only of files with frontal pose ('M+00').

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev').

    protocol
      One of the CAS-PEAL protocols ('accessory', 'aging', 'background', 'distance', 'expression', 'lighting', 'pose').
      Note: this field is ignored for group 'world'.
      Note: this field is ignored for purpose 'enroll'.

    purposes
      One or several purposes for which files should be retrieved ('enroll', 'probe').
      Note: this field is ignored for group 'world'.

    model_ids
      If given (as a list of model id's or a single one), only the files belonging to the specified model id is returned.
      For 'probe' purposes, this field is ignored since probe files are identical for all models.

    genders
      One or several of the genders ('F', 'M') of the clients.
      If not specified, objects of all genders are returned.

    ages
      One or several of the age ranges ('Y', 'M', 'O') of the clients.
      If not specified, objects of all age ranges are returned.

    lightings
      One or several of the possible lightings (e.g. 'EU+00' or 'FM-45').
      If not specified, objects of all lightings will be returned.
      Note: this field is ignored for purpose 'enroll'.

    poses
      One or several of the possible poses (e.g. 'M+00', 'U-67').
      If not specified, objects of all poses are returned.
      Note: this field is ignored for purpose 'enroll'.
      Note: for group 'world', only pose 'M+00' is available.

    expressions
      One or several expressions from ('N', 'L', 'F', 'S', 'C', 'O').
      If not specified, objects of all expressions are returned.
      Note: this field is ignored for purpose 'enroll'.

    accessories
      One or several accessories from (0, 1, 2, 3, 4, 5, 6).
      If not specified, objects of all accessories are returned.
      Note: this field is ignored for purpose 'enroll'.

    distances
      One or several distances from (0, 1, 2).
      If not specified, objects of all distances are returned.
      Note: this field is ignored for purpose 'enroll'.

    sessions
      One or several sessions from (0, 1, 2).
      If not specified, objects of all sessions are returned.
      Note: this field is ignored for purpose 'enroll'.

    backgrounds
      One or several backgrounds from ('B', 'R', 'D', 'Y', 'W').
      If not specified, objects of all backgrounds are returned.
      Note: this field is ignored for purpose 'enroll'.
    """

    # check that every parameter is as expected
    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    protocols = self.check_parameters_for_validity(
        protocol, "protocol", self.m_protocols)
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.m_purposes)
    genders = self.check_parameters_for_validity(
        genders, "gender", self.m_genders)
    ages = self.check_parameters_for_validity(ages, "age range", self.m_ages)
    lightings = self.check_parameters_for_validity(
        lightings, "lighting", self.m_lightings)
    poses = self.check_parameters_for_validity(poses, "pose", self.m_poses)
    expressions = self.check_parameters_for_validity(
        expressions, "expression", self.m_expressions)
    accessories = self.check_parameters_for_validity(
        accessories, "accessory", self.m_accessories)
    distances = self.check_parameters_for_validity(
        distances, "distance", self.m_distances)
    sessions = self.check_parameters_for_validity(
        sessions, "session", self.m_sessions)
    backgrounds = self.check_parameters_for_validity(
        backgrounds, "background", self.m_backgrounds)

    # assure that the given model ids are in an iteratable container
    if isinstance(model_ids, int):
      model_ids = (model_ids,)

    def _filter_some(query):
      # filter age and gender of the client
      return query.filter(Client.gender.in_(genders))\
                  .filter(Client.age.in_(ages))

    def _filter_all(query):
      # filter all information
      return _filter_some(query)\
          .filter(File.lighting.in_(lightings))\
          .filter(File.pose.in_(poses))\
          .filter(File.expression.in_(expressions))\
          .filter(File.accessory.in_(accessories))\
          .filter(File.distance.in_(distances))\
          .filter(File.session.in_(sessions))\
          .filter(File.background.in_(backgrounds))

    def _filter_models(query):
      # filter out the requested models
      if model_ids and len(model_ids):
        query = query.filter(Client.id.in_(model_ids))
      return query

    # collect the queries
    queries = []
    if 'world' in groups:
      queries.append(
          _filter_models(
              _filter_all(
                  self.query(File).join(Client)
                  .filter(File.purpose == 'world')
              )
          )
      )

    if 'dev' in groups:
      if 'enroll' in purposes:
        queries.append(
            _filter_models(
                _filter_some(
                    self.query(File).join(Client)
                    .filter(File.purpose == 'enroll')
                )
            )
        )

      if 'probe' in purposes:
        queries.append(
            _filter_all(
                self.query(File).join(Client).join(Protocol)
                .filter(File.purpose == 'probe')
                .filter(Protocol.name.in_(protocols))
            )
        )

    # we have collected all queries, now extract the File objects
    return [file for query in queries for file in query]

  def annotations(self, file):
    """Returns the annotations for the given file id as a dictionary {'reye':(y,x), 'leye':(y,x)}."""
    self.assert_validity()
    # return annotations as obtained from the __call__ command of the
    # Annotation class
    return file.annotation()

  def protocol_names(self):
    """Returns all registered protocol names"""
    return [str(p.name) for p in self.protocols()]

  def protocols(self):
    """Returns all registered protocols"""
    return list(self.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""
    return self.query(Protocol).filter(Protocol.name == name).count() != 0
