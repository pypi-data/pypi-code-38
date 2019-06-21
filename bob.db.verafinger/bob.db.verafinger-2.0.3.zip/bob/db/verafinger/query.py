#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Implementation of a simple database interface for querying PAD data'''


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


  def __init__(self, original_directory=None, original_extension=None):
    super(Database, self).__init__(SQLITE_FILE, File, original_directory,
        original_extension)


  def protocol_names(self):
    """Returns a list of all supported protocols"""

    return tuple([k.name for k in self.query(Protocol).order_by(Protocol.name)])


  def purposes(self):
    """Returns a list of all supported purposes"""

    return Subset.purpose_choices


  def groups(self):
    """Returns a list of all supported groups"""

    return Subset.group_choices


  def genders(self):
    """Returns a list of all supported gender values"""

    return Client.gender_choices


  def sides(self):
    """Returns a list of all supported side values"""

    return Finger.side_choices


  def sizes(self):
    """Returns a list of all supported size values"""

    return File.size_choices


  def sources(self):
    """Returns a list of all supported source values"""

    return File.source_choices


  def sessions(self):
    """Returns a list of all supported session values"""

    return File.session_choices


  def _finger_from_model_id(self, model_id):
    """Returns the first unique finger in the database given a ``model_id``"""

    return self.query(File).filter(File.model_id == model_id).first().finger


  def finger_name_from_model_id(self, model_id):
    """Returns the first unique finger name in the database given a ``model_id``"""

    return self._finger_from_model_id(model_id).unique_name


  def model_ids(self, protocol=None, groups=None):
    """Returns a set of models for a given protocol/group

    Parameters:

      protocol (:py:class:`str`, :py:class:`list`, optional): One or more of
        the supported protocols.  If not set, returns data from all protocols

      groups (:py:class:`str`, :py:class:`list`, optional): One or more of the
        supported groups. If not set, returns data from all groups. Notice this
        parameter should either not set or set to ``dev``. Otherwise, this
        method will return an empty list given we don't have a test set, only a
        development set.


    Returns:

      list: A list of string corresponding model identifiers with the specified
      filtering criteria

    """

    protocols = None
    if protocol:
      valid_protocols = self.protocol_names()
      protocols = self.check_parameters_for_validity(protocol, "protocol",
                                                     valid_protocols)

    if groups:
      valid_groups = self.groups()
      groups = self.check_parameters_for_validity(groups, "group",
                                                  valid_groups)

    retval = self.query(File)

    joins = []
    filters = []

    subquery = self.query(Subset)
    subfilters = []

    if protocols:
      subquery = subquery.join(Protocol)
      subfilters.append(Protocol.name.in_(protocols))

    if groups:
      subfilters.append(Subset.group.in_(groups))

    subfilters.append(Subset.purpose == 'enroll')

    subsets = subquery.filter(*subfilters)
    filters.append(File.subsets.any(Subset.id.in_([k.id for k in subsets])))

    retval = retval.join(*joins).filter(*filters).distinct().order_by('id')

    return sorted(set([k.model_id for k in retval.distinct()]))


  def objects(self, protocol=None, groups=None, purposes=None,
              model_ids=None, genders=None, sides=None, sizes=None,
              sources=None, sessions=None):
    """Returns objects filtered by criteria


    Parameters:

      protocol (:py:class:`str`, :py:class:`list`, optional): One or more of
        the supported protocols. If not set, returns data from all protocols

      groups (:py:class:`str`, :py:class:`list`, optional): One or more of the
        supported groups. If not set, returns data from all groups

      purposes (:py:class:`str`, :py:class:`list`, optional): One or more of
        the supported purposes. If not set, returns data for all purposes

      model_ids (:py:class:`str`, :py:class:`list`, optional): If set, limit
        output using the provided model identifiers

      genders (:py:class:`str`, :py:class:`list`, optional): If set, limit
        output using the provided gender identifiers

      sides (:py:class:`str`, :py:class:`list`, optional): If set, limit output
        using the provided side identifier

      sizes (:py:class:`str`, :py:class:`list`, optional): If set, limit output
        using the provided size identifier

      sources (:py:class:`str`, :py:class:`list`, optional): If set, limit
        output using the provided source identifier

      sessions (:py:class:`str`, :py:class:`list`, optional): If set, limit
        output using the provided session identifiers


    Returns:

      list: A list of :py:class:`File` objects corresponding to the filtering
      criteria.

    """

    protocols = None
    if protocol:
      valid_protocols = self.protocol_names()
      protocols = self.check_parameters_for_validity(protocol, "protocol",
                                                     valid_protocols)

    if groups:
      valid_groups = self.groups()
      groups = self.check_parameters_for_validity(
          groups, "group", valid_groups)

    if purposes:
      valid_purposes = self.purposes()
      purposes = self.check_parameters_for_validity(purposes, "purpose",
                                                    valid_purposes)

    # if only asking for 'probes', then ignore model_ids as all of our
    # protocols do a full probe-model scan
    if purposes and len(purposes) == 1 and 'probe' in purposes:
      model_ids = None

    if model_ids:
      valid_model_ids = self.model_ids(protocol, groups)
      model_ids = self.check_parameters_for_validity(model_ids, "model_ids",
                                                     valid_model_ids)

    if genders:
      valid_genders = self.genders()
      genders = self.check_parameters_for_validity(genders, "genders",
                                                   valid_genders)

    if sides:
      valid_sides = self.sides()
      sides = self.check_parameters_for_validity(sides, "sides", valid_sides)

    if sizes:
      valid_sizes = self.sizes()
      sizes = self.check_parameters_for_validity(sizes, "sizes", valid_sizes)

    if sources:
      valid_sources = self.sources()
      sources = self.check_parameters_for_validity(sources, "sources",
          valid_sources)

    if sessions:
      valid_sessions = self.sessions()
      sessions = self.check_parameters_for_validity(sessions, "sessions",
          valid_sessions)

    retval = self.query(File)

    joins = []
    filters = []

    if protocols or groups or purposes:

      subquery = self.query(Subset)
      subfilters = []

      if protocols:
        subquery = subquery.join(Protocol)
        subfilters.append(Protocol.name.in_(protocols))

      if groups:
        subfilters.append(Subset.group.in_(groups))
      if purposes:
        subfilters.append(Subset.purpose.in_(purposes))

      subsets = subquery.filter(*subfilters)

      filters.append(File.subsets.any(Subset.id.in_([k.id for k in subsets])))

    if genders or sides:
      joins.append(Finger)

      if genders:
        fingers = self.query(Finger).join(
            Client).filter(Client.gender.in_(genders))
        filters.append(Finger.id.in_([k.id for k in fingers]))

      if sides:
        filters.append(Finger.side.in_(sides))

    if sessions or sizes or sources:
      if sessions:
        filters.append(File.session.in_(sessions))

      if sizes:
        filters.append(File.size.in_(sizes))

      if sources:
        filters.append(File.source.in_(sources))

    if model_ids:
      if purposes and len(purposes) == 1 and 'attack' in purposes:
        filters.append(File.finger_id.in_([self._finger_from_model_id(k).id for k in model_ids]))
      else:
        filters.append(File.model_id.in_(model_ids))

    retval = retval.join(*joins).filter(*filters).distinct().order_by('id')

    return list(retval)
