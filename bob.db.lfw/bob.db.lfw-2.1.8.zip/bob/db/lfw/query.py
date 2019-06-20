#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Thu May 24 10:41:42 CEST 2012
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

"""This module provides the Dataset interface allowing the user to query the
LFW database.
"""

import six
from bob.db.base import utils
from .models import *
from sqlalchemy.orm import aliased
from .driver import Interface

import bob.db.base

SQLITE_FILE = Interface().files()[0]


class Database(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension='.jpg', annotation_type=None):
    # call base class constructor
    super(Database, self).__init__(SQLITE_FILE, File,
                                   original_directory, original_extension)

    self.m_valid_protocols = ('view1', 'fold1', 'fold2', 'fold3',
                              'fold4', 'fold5', 'fold6', 'fold7', 'fold8', 'fold9', 'fold10')
    self.m_valid_groups = ('world', 'dev', 'eval')
    self.m_valid_purposes = ('enroll', 'probe')
    self.m_valid_classes = ('matched', 'client', 'unmatched', 'impostor')
    self.m_subworld_counts = {'onefolds': 1, 'twofolds': 2, 'threefolds': 3,
                              'fourfolds': 4, 'fivefolds': 5, 'sixfolds': 6, 'sevenfolds': 7}
    self.m_valid_types = ('restricted', 'unrestricted')

    self.m_valid_annotation_types = ('idiap', 'funneled')
    if annotation_type is not None:
      self.m_annotation_type = self.check_parameter_for_validity(
          annotation_type, "annotation type", self.m_valid_annotation_types)
    else:
      self.m_annotation_type = None

  def __eval__(self, fold):
    return int(fold[4:])

  def __dev__(self, eval):
    # take the two parts of the training set (the ones before the eval set)
    # for dev
    return ((eval + 7) % 10 + 1, (eval + 8) % 10 + 1)

  def __dev_for__(self, fold):
    return ["fold%d" % f for f in self.__dev__(self.__eval__(fold))]

  def __world_for__(self, fold, subworld):
    # the training sets for each fold are composed of all folds
    # except the given one and the previous
    eval = self.__eval__(fold)
    dev = self.__dev__(eval)
    world_count = self.m_subworld_counts[subworld]
    world = []
    for i in range(world_count):
      world.append((eval + i) % 10 + 1)
    return ["fold%d" % f for f in world]

  def protocol_names(self):
    """Returns the names of the valid protocols."""
    return self.m_valid_protocols

  def groups(self, protocol=None):
    """Returns the groups, which are available in the database."""
    if protocol != 'view1':
      return self.m_valid_groups
    else:
      return self.m_valid_groups[:2]

  def subworld_names(self, protocol=None):
    """Returns all valid sub-worlds for the fold.. protocols; for view1 an empty list is returned."""
    if protocol != 'view1':
      return self.m_subworld_counts.keys()
    else:
      return []

  def world_types(self):
    """Returns the valid types of worlds: ('restricted', 'unrestricted')."""
    return self.m_valid_types

  def annotation_types(self):
    """Queries the database for the available types of annotations."""
    s = set([a.annotation_type for a in self.query(Annotation)])
    return [str(t) for t in s]

  def clients(self, protocol=None, groups=None, subworld='sevenfolds', world_type='unrestricted'):
    """Returns a list of Client objects for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider; one of: ('view1', 'fold1', ..., 'fold10'), or None

    groups
      The groups to which the clients belong; one or several of: ('world', 'dev', 'eval')
      Note: the 'eval' group does not exist for protocol 'view1'.

    subworld
      The subset of the training data. Has to be specified if groups includes 'world'
      and protocol is one of 'fold1', ..., 'fold10'.
      It might be exactly one of ('onefolds', 'twofolds', ..., 'sevenfolds').
      Ignored for group 'dev' and 'eval'.

    world_type
      One of ('restricted', 'unrestricted'). If 'restricted' (the default), only the
      clients that are used in one of the training pairs are returned. For 'unrestricted',
      all training people are returned.
      Ignored for group 'dev' and 'eval'.

    Returns: A list containing all Client objects which have the desired properties.
    """
    protocols = self.check_parameters_for_validity(
        protocol, 'protocol', self.m_valid_protocols)
    groups = self.check_parameters_for_validity(
        groups, 'group', self.m_valid_groups)
    if subworld != None:
      subworld = self.check_parameter_for_validity(
          subworld, 'sub-world', list(self.m_subworld_counts.keys()))
    world_type = self.check_parameter_for_validity(
        world_type, 'training type', self.m_valid_types)

    queries = []

    # List of the clients
    for protocol in protocols:
      if protocol == 'view1':
        if 'world' in groups:
          if world_type == 'restricted':
            queries.append(
                self.query(Client).join(File).join((Pair, or_(File.id == Pair.enroll_file_id, File.id == Pair.probe_file_id))).
                filter(Pair.protocol == 'train').
                order_by(Client.id))
          else:
            queries.append(
                self.query(Client).join(File).join(People).
                filter(People.protocol == 'train').
                order_by(Client.id))
        if 'dev' in groups:
          queries.append(
              self.query(Client).join(File).join(People).
              filter(People.protocol == 'test').
              order_by(Client.id))
      else:
        if 'world' in groups:
          # select training set for the given fold
          trainset = self.__world_for__(protocol, subworld)
          if world_type == 'restricted':
            queries.append(
                self.query(Client).join(File).join((Pair, or_(File.id == Pair.enroll_file_id, File.id == Pair.probe_file_id))).
                filter(Pair.protocol.in_(trainset)).
                order_by(Client.id))
          else:
            queries.append(
                self.query(Client).join(File).join(People).
                filter(People.protocol.in_(trainset)).
                order_by(Client.id))
        if 'dev' in groups:
          # select development set for the given fold
          devset = self.__dev_for__(protocol)
          queries.append(
              self.query(Client).join(File).join(People).
              filter(People.protocol.in_(devset)).
              order_by(Client.id))
        if 'eval' in groups:
          queries.append(
              self.query(Client).join(File).join(People).
              filter(People.protocol == protocol).
              order_by(Client.id))

    # all queries are made; now collect the clients
    retval = []
    for query in queries:
      for client in query:
        retval.append(client)

    return self.uniquify(retval)

  def models(self, protocol=None, groups=None):
    """Returns a list of File objects (there are multiple models per client) for the specific query by the user.
    For the 'dev' and 'eval' groups,  the first element of each pair is extracted.

    Keyword Parameters:

    protocol
      The protocol to consider; one of: ('view1', 'fold1', ..., 'fold10'), or None

    groups
      The groups to which the clients belong; one or several of: ('dev', 'eval')
      The 'eval' group does not exist for protocol 'view1'.

    Returns: A list containing all File objects which have the desired properties.
    """

    protocols = self.check_parameters_for_validity(
        protocol, 'protocol', self.m_valid_protocols)
    groups = self.check_parameters_for_validity(
        groups, 'group', ('dev', 'eval'))

    # the restricted case...
    queries = []

    # List of the models
    for protocol in protocols:
      if protocol == 'view1':
        if 'dev' in groups:
          queries.append(\
              # enroll files
              self.query(File).join((Pair, File.id == Pair.enroll_file_id)).\
              filter(Pair.protocol == 'test'))
      else:
        if 'dev' in groups:
          # select development set for the given fold
          devset = self.__dev_for__(protocol)
          queries.append(
              self.query(File).join((Pair, File.id == Pair.enroll_file_id)).
              filter(Pair.protocol.in_(devset)))
        if 'eval' in groups:
          queries.append(
              self.query(File).join((Pair, File.id == Pair.enroll_file_id)).
              filter(Pair.protocol == protocol))

    # all queries are made; now collect the files
    retval = []
    for query in queries:
      retval.extend([file for file in query])

    return self.uniquify(retval)

  def model_ids(self, protocol=None, groups=None):
    """Returns a list of model ids for the specific query by the user.
    For the 'dev' and 'eval' groups, the first element of each pair is extracted.

    Keyword Parameters:

    protocol
      The protocol to consider; one of: ('view1', 'fold1', ..., 'fold10'), or None

    groups
      The groups to which the clients belong; one or several of: ('dev', 'eval')
      The 'eval' group does not exist for protocol 'view1'.

    Returns: A list containing all model ids which have the desired properties.
    """
    return [file.id for file in self.models(protocol, groups)]

  def get_client_id_from_file_id(self, file_id, **kwargs):
    """Returns the client_id (real client id) attached to the given file_id

    Keyword Parameters:

    file_id
      The file_id to consider

    Returns: The client_id attached to the given file_id
    """
    self.assert_validity()

    q = self.query(File).\
        filter(File.id == file_id)

    assert q.count() == 1
    return q.first().client_id

  def get_client_id_from_model_id(self, model_id, **kwargs):
    """Returns the client_id (real client id) attached to the given model id

    Keyword Parameters:

    model_id
      The model to consider

    type
      One of ('restricted', 'unrestricted'). If the type 'restricted' is given,
      model_ids will be handled as file ids, if type is 'unrestricted', model ids
      will be client ids.

    Returns: The client_id attached to the given model
    """

    # since there is one model per file, we can re-use the function above.
    return self.get_client_id_from_file_id(model_id)

  def objects(self, protocol=None, model_ids=None, groups=None, purposes=None, subworld='sevenfolds', world_type='unrestricted'):
    """Returns a list of File objects for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('view1', 'fold1', ..., 'fold10'), or None

    groups
      The groups to which the objects belong ('world', 'dev', 'eval')

    purposes
      The purposes of the objects ('enroll', 'probe')

    subworld
      The subset of the training data. Has to be specified if groups includes 'world'
      and protocol is one of 'fold1', ..., 'fold10'.
      It might be exactly one of ('onefolds', 'twofolds', ..., 'sevenfolds').

    world_type
      One of ('restricted', 'unrestricted'). If 'restricted', only the files that
      are used in one of the training pairs are used. For 'unrestricted', all
      files of the training people are returned.

    model_ids
      Only retrieves the objects for the provided list of model ids.
      If 'None' is given (this is the default), no filter over the model_ids is performed.
      Note that the combination of 'world' group and 'model_ids' should be avoided.

    Returns: A list of File objects considering all the filtering criteria.
    """

    protocols = self.check_parameters_for_validity(
        protocol, "protocol", self.m_valid_protocols)
    groups = self.check_parameters_for_validity(
        groups, "group", self.m_valid_groups)
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.m_valid_purposes)
    world_type = self.check_parameter_for_validity(
        world_type, 'training type', self.m_valid_types)

    if subworld != None:
      subworld = self.check_parameter_for_validity(
          subworld, 'sub-world', list(self.m_subworld_counts.keys()))

    if(isinstance(model_ids, six.string_types)):
      model_ids = (model_ids,)

    queries = []
    probe_queries = []
    file_alias = aliased(File)

    for protocol in protocols:
      if protocol == 'view1':
        if 'world' in groups:
          # training files of view1
          if world_type == 'restricted':
            queries.append(
                self.query(File).join((Pair, or_(File.id == Pair.enroll_file_id, File.id == Pair.probe_file_id))).
                filter(Pair.protocol == 'train'))
          else:
            queries.append(
                self.query(File).join(People).
                filter(People.protocol == 'train'))
        if 'dev' in groups:
          # test files of view1
          if 'enroll' in purposes:
            queries.append(
                self.query(File).join((Pair, File.id == Pair.enroll_file_id)).
                filter(Pair.protocol == 'test'))
          if 'probe' in purposes:
            probe_queries.append(
                self.query(File).
                join((Pair, File.id == Pair.probe_file_id)).
                join((file_alias, Pair.enroll_file_id == file_alias.id)).
                filter(Pair.protocol == 'test'))

      else:
        # view 2
        if 'world' in groups:
          # world set of current fold of view 2
          trainset = self.__world_for__(protocol, subworld)
          if world_type == 'restricted':
            queries.append(
                self.query(File).join((Pair, or_(File.id == Pair.enroll_file_id, File.id == Pair.probe_file_id))).
                filter(Pair.protocol.in_(trainset)))
          else:
            queries.append(
                self.query(File).join(People).
                filter(People.protocol.in_(trainset)))

        if 'dev' in groups:
          # development set of current fold of view 2
          devset = self.__dev_for__(protocol)
          if 'enroll' in purposes:
            queries.append(
                self.query(File).join((Pair, File.id == Pair.enroll_file_id)).
                filter(Pair.protocol.in_(devset)))
          if 'probe' in purposes:
            probe_queries.append(
                self.query(File).
                join((Pair, File.id == Pair.probe_file_id)).
                join((file_alias, file_alias.id == Pair.enroll_file_id)).
                filter(Pair.protocol.in_(devset)))

        if 'eval' in groups:
          # evaluation set of current fold of view 2; this is the REAL fold
          if 'enroll' in purposes:
            queries.append(
                self.query(File).join((Pair, File.id == Pair.enroll_file_id)).
                filter(Pair.protocol == protocol))
          if 'probe' in purposes:
            probe_queries.append(
                self.query(File).
                join((Pair, File.id == Pair.probe_file_id)).
                join((file_alias, file_alias.id == Pair.enroll_file_id)).
                filter(Pair.protocol == protocol))

    retval = []
    for query in queries:
      if model_ids and len(model_ids):
        query = query.filter(File.id.in_(model_ids))

      retval.extend([file for file in query])

    for query in probe_queries:
      if model_ids and len(model_ids):
        query = query.filter(file_alias.id.in_(model_ids))

      for probe in query:
        retval.append(probe)

    return self.uniquify(retval)

  def pairs(self, protocol=None, groups=None, classes=None, subworld='sevenfolds'):
    """Queries a list of Pair's of files.

    Keyword Parameters:

    protocol
      The protocol to consider ('view1', 'fold1', ..., 'fold10')

    groups
      The groups to which the objects belong ('world', 'dev', 'eval')

    classes
      The classes to which the pairs belong ('matched', 'unmatched'), or ('client', 'impostor')

    subworld
      The subset of the training data. Has to be specified if groups includes 'world'
      and protocol is one of 'fold1', ..., 'fold10'.
      It might be exactly one of ('onefolds', 'twofolds', ..., 'sevenfolds').

    Returns: A list of Pair's considering all the filtering criteria.
    """

    def default_query():
      return self.query(Pair).\
          join((File1, File1.id == Pair.enroll_file_id)).\
          join((File2, File2.id == Pair.probe_file_id))

    protocol = self.check_parameter_for_validity(
        protocol, "protocol", self.m_valid_protocols)
    groups = self.check_parameters_for_validity(
        groups, "group", self.m_valid_groups)
    classes = self.check_parameters_for_validity(
        classes, "class", self.m_valid_classes)
    if subworld != None:
      subworld = self.check_parameter_for_validity(
          subworld, 'sub-world', list(self.m_subworld_counts.keys()))

    queries = []
    File1 = aliased(File)
    File2 = aliased(File)

    if protocol == 'view1':
      if 'world' in groups:
        queries.append(default_query().filter(Pair.protocol == 'train'))
      if 'dev' in groups:
        queries.append(default_query().filter(Pair.protocol == 'test'))

    else:
      if 'world' in groups:
        trainset = self.__world_for__(protocol, subworld)
        queries.append(default_query().filter(Pair.protocol.in_(trainset)))
      if 'dev' in groups:
        devset = self.__dev_for__(protocol)
        queries.append(default_query().filter(Pair.protocol.in_(devset)))
      if 'eval' in groups:
        queries.append(default_query().filter(Pair.protocol == protocol))

    retval = []
    for query in queries:
      if 'matched' not in classes and 'client' not in classes:
        query = query.filter(Pair.is_match == False)
      if 'unmatched' not in classes and 'impostor' not in classes:
        query = query.filter(Pair.is_match == True)

      for pair in query:
        retval.append(pair)

    return retval

  def annotations(self, file, annotation_type=None):
    """Returns the annotations for the given file id as a dictionary, e.g. {'reye':(y,x), 'leye':(y,x)}.

    Keyword parameters:

    file_id
      The ``File`` object for which you want to retrieve the annotations

    annotation_type
      The type of annotations ('idiap', 'funneled').
      If not specified, and if not given in the constructor, all annotations are taken, which might to cause an assertion error.
    """
    self.assert_validity()
    if annotation_type is None:
      annotation_type = self.m_annotation_type

    annotation_type = self.check_parameters_for_validity(
        annotation_type, "annotation type", self.m_valid_annotation_types)

    query = self.query(Annotation).filter(Annotation.annotation_type.in_(
        annotation_type)).join(File).filter(File.id == file.id)
    assert query.count() == 1
    annotation = query.first()

    # return the annotations as returned by the call function of the
    # Annotation object
    return annotation()

  def t_model_ids(self, protocol, groups='dev', **kwargs):
    """Returns the list of model ids used for T-Norm of the given protocol for the given group that satisfy your query."""
    return self.uniquify(self.tmodel_ids(protocol=protocol, groups=groups, **kwargs))

  def t_enroll_files(self, protocol, model_id, groups='dev', **kwargs):
    """Returns the list of T-Norm model enrollment File objects from the given model id of the given protocol for the given group that satisfy your query."""
    return self.uniquify(self.tobjects(protocol=protocol, groups=groups, model_ids=(model_id,), **kwargs))

  def z_probe_files(self, protocol, groups='dev', **kwargs):
    """Returns the list of Z-Norm probe File objects to probe the model with the given model id of the given protocol for the given group that satisfy your query."""
    return self.uniquify(self.zobjects(protocol=protocol, groups=groups, **kwargs))
