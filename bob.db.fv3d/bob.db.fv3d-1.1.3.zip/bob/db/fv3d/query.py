#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Dataset interface allowing the user to query the VERA database"""

import six
from .models import *
from .driver import Interface
from sqlalchemy import and_, not_

import bob.core
logger = bob.core.log.setup(__name__)

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

    return ('train', 'enroll', 'probe')


  def groups(self):
    """Returns a list of all supported groups"""

    return ('train', 'dev', 'eval')


  def genders(self):
    """Returns a list of all supported gender values"""

    return Client.gender_choices


  def sides(self):
    """Returns a list of all supported side values"""

    return Finger.side_choices


  def fingers(self):
    """Returns a list of all supported finger values"""

    return Finger.name_choices


  def sessions(self):
    """Returns a list of all supported session values"""

    return File.session_choices


  def finger_name_from_model_id(self, model_id):
    """Returns the unique finger name in the database given a ``model_id``"""

    model = self.query(Model).filter(Model.name==model_id).first()
    return model.finger.unique_name


  def model_ids(self, protocol=None, groups=None):
    """Returns a set of models identifiers for a given protocol/group

    Parameters:

      protocol (:py:class:`str`, :py:class:`list`, optional): One or more of
        the supported protocols.  If not set, returns data from all protocols

      groups (:py:class:`str`, :py:class:`list`, optional): One or more of the
        supported groups. If not set, returns data from all groups. Notice this
        parameter should either not set or set to ``dev``, ``eval`` or an
        iterator that yields both.


    Returns:

      list: A list of string corresponding model identifiers with the specified
      filtering criteria

    """

    if groups and 'train' in groups:
      # there are no models in the training set
      if len(groups) == 1: return [] #only group required, so return empty
      groups = tuple(k for k in groups if k != 'train')

    valid_protocols = self.protocol_names()
    protocols = bob.db.base.utils.check_parameters_for_validity(protocol,
        "protocol", valid_protocols)

    valid_groups = Model.group_choices
    groups = bob.db.base.utils.check_parameters_for_validity(groups, "group",
        valid_groups)

    retval = self.query(Model).join(Protocol)
    retval = retval.filter(Protocol.name.in_(protocols))

    if groups:
      retval = retval.filter(Model.group.in_(groups))

    retval = retval.distinct().order_by('id')

    return [k.name for k in retval]


  def _train_objects(self, protocols, genders, sides, fingers, sessions):
    """Returns a query that yields objects related to training

    This is a private function, input parameters are assumed pre-checked
    """

    return query


  def objects(self, protocol=None, groups=None, purposes=None,
      model_ids=None, genders=None, sides=None, fingers=None, sessions=None):
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

      fingers (:py:class:`str`, :py:class:`list`, optional): If set, limit
        output using the provided finger identifiers

      sessions (:py:class:`str`, :py:class:`list`, optional): If set, limit
        output using the provided session identifiers


    Returns:

      list: A list of :py:class:`File` objects corresponding to the filtering
      criteria.

    """

    valid_protocols = self.protocol_names()
    protocols = bob.db.base.utils.check_parameters_for_validity(protocol,
        "protocol", valid_protocols)

    valid_groups = self.groups()
    groups = bob.db.base.utils.check_parameters_for_validity(groups, "group",
        valid_groups)

    valid_purposes = self.purposes()
    purposes = bob.db.base.utils.check_parameters_for_validity(purposes,
        "purpose", valid_purposes)

    # cleans up groups and purposes to solve for the minimum
    if ('train' in purposes and not ('train' in groups)):
      purposes = tuple(k for k in purposes if k != 'train')
    if ('train' in groups and not ('train' in purposes)):
      groups = tuple(k for k in groups if k != 'train')
    if ('enroll' in purposes or 'probe' in purposes) and not 'dev' in groups:
      purposes = tuple(k for k in purposes if k not in ['enroll', 'probe'])
    if 'dev' in groups and not ('enroll' in purposes or 'probe' in purposes):
      groups = tuple(k for k in groups if k != 'dev')

    # if only asking for 'probes', then ignore model_ids as all of our
    # protocols do a full probe-model scan
    if purposes and len(purposes) == 1 and 'probe' in purposes:
      model_ids = None

    if model_ids:
      valid_model_ids = self.model_ids(protocol, groups)
      model_ids = bob.db.base.utils.check_parameters_for_validity(model_ids,
          "model_ids", valid_model_ids)

    valid_genders = self.genders()
    genders = bob.db.base.utils.check_parameters_for_validity(genders,
        "genders", valid_genders)

    valid_fingers = self.fingers()
    fingers = bob.db.base.utils.check_parameters_for_validity(fingers,
        "fingers", valid_fingers)

    valid_sides = self.sides()
    sides = bob.db.base.utils.check_parameters_for_validity(sides, "sides",
        valid_sides)

    valid_sessions = self.sessions()
    sessions = bob.db.base.utils.check_parameters_for_validity(sessions,
        "sessions", valid_sessions)

    # this database contains 3 sets of "files" for each protocol: the ones
    # related to the training_set, models and probes related to both dev and
    # eval groups. These file lists don't overlap

    retval = set()

    if 'train' in purposes:
      q = self.query(File).join(Protocol.training_set)
      q = q.join(Finger).join(Client)
      q = q.filter(Protocol.name.in_(protocols))
      q = q.filter(Client.gender.in_(genders))
      q = q.filter(Finger.side.in_(sides))
      q = q.filter(Finger.name.in_(fingers))
      q = q.filter(File.session.in_(sessions))
      retval.update(q)

    # get identities for the protocol in order to simplify query
    protocol_ids = self.query(Protocol).filter(Protocol.name.in_(protocols))
    protocol_ids = [k.id for k in protocol_ids]

    if 'enroll' in purposes:
      q = self.query(File).join(Model.files)
      q = q.join(Finger).join(Client)
      q = q.filter(Model.group.in_(groups))
      if model_ids: q = q.filter(Model.name.in_(model_ids))
      q = q.filter(Model.protocol_id.in_(protocol_ids))
      q = q.filter(Client.gender.in_(genders))
      q = q.filter(Finger.side.in_(sides))
      q = q.filter(Finger.name.in_(fingers))
      q = q.filter(File.session.in_(sessions))
      retval.update(q)

    if 'probe' in purposes:
      q = self.query(File).join(Probe.file)
      q = q.join(Finger).join(Client)
      q = q.filter(Probe.group.in_(groups))
      q = q.filter(Probe.protocol_id.in_(protocol_ids))
      q = q.filter(Client.gender.in_(genders))
      q = q.filter(Finger.side.in_(sides))
      q = q.filter(Finger.name.in_(fingers))
      q = q.filter(File.session.in_(sessions))
      retval.update(q)

    # combine all queries, sort and uniq'fy
    return sorted(retval, key=lambda x: x.path)
