#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
#
# Copyright (C) 2012-2014 Idiap Research Institute, Martigny, Switzerland
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
NIST SRE 2012 database in the most obvious ways.
"""

import os
from .models import *
from .driver import Interface

import bob.db.base

import bob.core
logger = bob.core.log.setup("bob.db.nist_sre12")

SQLITE_FILE = Interface().files()[0]

try:
  basestring
except NameError:
  basestring = str


class Database(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory=None, original_extension=".sph"):
    # call base class constructors
    bob.db.base.SQLiteDatabase.__init__(
        self, SQLITE_FILE, File, original_directory, original_extension)

  def groups(self, protocol=None):
    """Returns the names of all registered groups"""

    # Same as Model.group_choices for this database
    return ProtocolPurpose.group_choices

  def genders(self):
    """Returns the names of all registered groups"""

    return ('male', 'female')

  def clients(self, protocol=None, groups=None, filter_ids_unknown=True):
    """Returns a set of clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('female', 'male')

    groups
      The groups to which the clients belong ('core-all')

    filter_ids_unknown
      Do not add the ids unknown 'F_ID_X_F' and 'M_ID_X_M'

    Returns: A list containing all the clients which have the given properties.
    """

    return self.models(protocol, groups, filter_ids_unknown)

  def models(self, protocol=None, groups=None, filter_ids_unknown=True):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('female', 'male')

    groups
      The groups to which the subjects attached to the models belong ('eval')

    filter_ids_unknown
      Do not add the ids unknown 'F_ID_X' and 'M_ID_X'

    Returns: A list containing all the models belonging to the given group.
    """
    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names())
    groups = self.check_parameters_for_validity(
        groups, "groups", self.groups())

    # List of the clients
    retval = []
    q = self.query(Model).join((ProtocolPurpose, Model.protocolPurposes)).join((Protocol, ProtocolPurpose.protocol)).\
        filter(Protocol.name.in_(protocol)).filter(ProtocolPurpose.sgroup.in_(
            groups)).filter(ProtocolPurpose.purpose == 'enroll')
    if filter_ids_unknown == True:
      q = q.filter(not_(Model.id.in_(['F_ID_X', 'M_ID_X'])))
    q = q.order_by(Model.id)
    retval += list(q)

    return list(set(retval))

  def model_ids(self, protocol=None, groups=None, filter_ids_unknown=True):
    """Returns a list of model ids for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('female', 'male')

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    filter_ids_unknown
      Do not add the ids unknown 'F_ID_X' and 'M_ID_X'

    Returns: A list containing the ids of all models belonging to the given group.
    """

    return [model.id for model in self.models(protocol, groups, filter_ids_unknown)]

  def client_ids(self, protocol=None, groups=None, filter_ids_unknown=True):
    """Returns a list of client ids for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('female', 'male')

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    filter_ids_unknown
      Do not add the ids unknown 'F_ID_X' and 'M_ID_X'

    Returns: A list containing the ids of all clients belonging to the given group.
    """
    return list(set([model.client_id for model in self.models(protocol, groups, filter_ids_unknown)]))

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    return self.query(Model).filter(Model.id == id).count() != 0

  def client(self, id):
    """Returns the client object in the database given a certain id. Raises
    an error if that does not exist."""

    return self.query(Model).filter(Model.client_id == id).one()

  def get_client_id_from_model_id(self, model_id, **kwargs):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model_id to consider

    Returns: The client_id attached to the given model_id
    """
    model = self.query(Model).filter(Model.model_id == model_id).one()
    return model.client_id

  def objects(self, protocol=None, purposes=None, model_ids=None, groups=None, gender=None):
    """Returns a set of filenames for the specific query by the user.
    WARNING: Files used as impostor access for several different models are
    only listed one and refer to only a single model

    Keyword Parameters:

    protocol
      The protocol to consider ('female', 'male')

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
      One of the groups ('dev', 'eval', 'world', 'optional_world_1', 'optional_world_2') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor')
      or a tuple with several of them. If 'None' is given (this is the
      default), it is considered the same as a tuple with all possible values.

    Returns: A list of files which have the given properties.
    """

    protocol = self.check_parameters_for_validity(
        protocol, "protocol", self.protocol_names(), 'core-all')
    purposes = self.check_parameters_for_validity(
        purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())

    if (model_ids is None):
      model_ids = ()
    elif (isinstance(model_ids, basestring)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []

    if('enroll' in purposes):

      if model_ids == ():
        if gender == None:
          q1l = self.query(ModelEnrollLink).join(Protocol).filter(
              Protocol.name.in_(protocol)).distinct().all()
        else:
          q1l = self.query(ModelEnrollLink).join(Model).join(Protocol).filter(
              and_(Protocol.name.in_(protocol), Model.gender == gender)).distinct().all()
        if len(q1l) > 0:
          file_ids_big = [x.file_id for x in q1l]
          length = len(file_ids_big)
          batches = int(length / 999) + 1  # 999 is the limit of sqlite in in_
          for i in range(batches):
            logger.info(
                'querying batch {} of {} batches'.format(i + 1, batches))
            file_ids = file_ids_big[i * 999:(i + 1) * 999]
            if not file_ids:
              continue
            q = self.query(File).filter(
                File.id.in_(file_ids)).order_by(File.id)
            if q.count() > 0:
              retval += list(q)

      else:
        if gender == None:
          q1l = self.query(ModelEnrollLink).join(Protocol).filter(
              and_(ModelEnrollLink.model_id.in_(model_ids), Protocol.name.in_(protocol))).all()
        else:
          q1l = self.query(ModelEnrollLink).join(Model).join(Protocol).filter(and_(ModelEnrollLink.model_id.in_(
              model_ids), Protocol.name.in_(protocol), Model.gender == gender)).distinct().all()
        if len(q1l) > 0:
          file_ids_big = [x.file_id for x in q1l]
          length = len(file_ids_big)
          batches = int(length / 999) + 1  # 999 is the limit of sqlite in in_
          for i in range(batches):
            logger.info(
                'querying batch {} of {} batches'.format(i + 1, batches))
            file_ids = file_ids_big[i * 999:(i + 1) * 999]
            if not file_ids:
              continue
            q = self.query(File).filter(
                File.id.in_(file_ids)).order_by(File.id)
            if q.count() > 0:
              retval += list(q)

    if('probe' in purposes):
      if model_ids == ():
        if gender == None:
          q = self.query(File).join((ProtocolPurpose, File.protocolPurposes)).join(
              Protocol).filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.purpose == 'probe'))
          if q.count() > 0:
            retval += list(q)
        else:
          #          import ipdb ; ipdb.set_trace()
          q1l = self.query(ModelProbeLink).join(Model).join(Protocol).filter(
              and_(Protocol.name.in_(protocol), Model.gender == gender)).all()
          if len(q1l) > 0:
            file_ids_big = list(set([x.file_id for x in q1l]))
            length = len(file_ids_big)
            # 999 is the limit of sqlite in in_
            batches = int(length / 999) + 1
            for i in range(batches):
              logger.info(
                  'querying batch {} of {} batches'.format(i + 1, batches))
              file_ids = file_ids_big[i * 999:(i + 1) * 999]
              if not file_ids:
                continue
              q = self.query(File).filter(
                  File.id.in_(file_ids)).order_by(File.id)
              if q.count() > 0:
                retval += list(q)
      else:
        if gender == None:
          q1l = self.query(ModelProbeLink).join(Protocol).filter(and_(
              ModelProbeLink.model_id.in_(model_ids), Protocol.name.in_(protocol))).distinct().all()
        else:
          q1l = self.query(ModelProbeLink).join(Protocol).filter(and_(ModelProbeLink.model_id.in_(
              model_ids), Protocol.name.in_(protocol), Model.gender == gender)).distinct().all()
        if len(q1l) > 0:
          file_ids_big = list(set([x.file_id for x in q1l]))
          length = len(file_ids_big)
          batches = int(length / 999) + 1  # 999 is the limit of sqlite in in_
          for i in range(batches):
            logger.info(
                'querying batch {} of {} batches'.format(i + 1, batches))
            file_ids = file_ids_big[i * 999:(i + 1) * 999]
            if not file_ids:
              continue
            q = self.query(File).filter(
                File.id.in_(file_ids)).order_by(File.id)
            if q.count() > 0:
              retval += list(q)

    return list(set(retval))  # To remove duplicates

  def protocol_names(self):
    """Returns all registered protocol names"""

    return [str(p.name) for p in self.protocols()]

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
