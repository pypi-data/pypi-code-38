#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Dataset interface allowing the user to query the VERA database"""

from .models import *
from .driver import Interface

import bob.db.base

SQLITE_FILE = Interface().files()[0]


class PADDatabase(bob.db.base.SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """


  def __init__(self, original_directory=None, original_extension=None):
    super(PADDatabase, self).__init__(SQLITE_FILE, File, original_directory,
        original_extension)


  def protocol_names(self):
    """Returns a list of all supported protocols"""

    return tuple([k.name for k in self.query(PADProtocol).order_by(PADProtocol.name)])


  def purposes(self):
    """Returns a list of all supported purposes"""

    return PADSubset.purpose_choices


  def groups(self):
    """Returns a list of all supported groups"""

    return PADSubset.group_choices


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


  def objects(self, protocol=None, groups=None, purposes=None, genders=None,
      sides=None, sizes=None, sources=None, sessions=None):
    """Returns objects filtered by criteria


    Parameters:

      protocol (:py:class:`str`, :py:class:`list`, optional): One or more of
        the supported protocols. If not set, returns data from all protocols

      groups (:py:class:`str`, :py:class:`list`, optional): One or more of the
        supported groups. If not set, returns data from all groups

      purposes (:py:class:`str`, :py:class:`list`, optional): One or more of
        the supported purposes. If not set, returns data for all purposes

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

      subquery = self.query(PADSubset)
      subfilters = []

      if protocols:
        subquery = subquery.join(PADProtocol)
        subfilters.append(PADProtocol.name.in_(protocols))

      if groups:
        subfilters.append(PADSubset.group.in_(groups))
      if purposes:
        subfilters.append(PADSubset.purpose.in_(purposes))

      padsubsets = subquery.filter(*subfilters)

      filters.append(File.padsubsets.any(PADSubset.id.in_([k.id for k in padsubsets])))

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

    retval = retval.join(*joins).filter(*filters).distinct().order_by('id')

    return list(retval)
