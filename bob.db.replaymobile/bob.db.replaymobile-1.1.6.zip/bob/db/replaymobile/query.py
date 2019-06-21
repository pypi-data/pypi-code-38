#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This module provides the Dataset interface allowing the user to query the
replay mobile database in the most obvious ways.
"""

import os
from bob.db.base import utils, SQLiteDatabase
from bob.extension import rc
from .models import *
from .driver import Interface

INFO = Interface()

SQLITE_FILE = INFO.files()[0]


class Database(SQLiteDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self,
               original_directory=rc['bob.db.replaymobile.directory'],
               original_extension='.mov',
               annotation_directory=None,
               annotation_extension='.json',
               annotation_type='json',
               ):
    # opens a session to the database - keep it open until the end
    super(Database, self).__init__(
        SQLITE_FILE, File, original_directory, original_extension)
    self.annotation_directory = annotation_directory
    self.annotation_extension = annotation_extension
    self.annotation_type = annotation_type

  def objects(self, support=Attack.attack_support_choices,
              protocol='grandtest', groups=Client.set_choices, cls=('attack', 'real'),
              light=File.light_choices, clients=None, device=File.device_choices, sample_type=Attack.sample_type_choices):
    """Returns a list of unique :py:class:`.File` objects for the specific
    query by the user.

    Keyword parameters:

    support
      One of the valid support types as returned by attack_supports() or all,
      as a tuple.  If you set this parameter to an empty string or the value
      None, we use reset it to the default, which is to get all.

    protocol
      The protocol for the attack. One of the ones returned by protocols(). If
      you set this parameter to an empty string or the value None, we use reset
      it to the default, "grandtest".

    groups
      One of the protocolar subgroups of data as returned by groups() or a
      tuple with several of them.  If you set this parameter to an empty string
      or the value None, we use reset it to the default which is to get all.

    cls
      Either "attack", "real", "enroll" or any combination of those (in a
      tuple). Defines the class of data to be retrieved.  If you set this
      parameter to an empty string or the value None, we use reset it to the
      default, ("real", "attack").

    light
      One of the lighting conditions as returned by lights() or a combination
      of the two (in a tuple), which is also the default.

    clients
      If set, should be a single integer or a list of integers that define the
      client identifiers from which files should be retrieved. If ommited, set
      to None or an empty list, then data from all clients is retrieved.

    device
      One of the capture device as returned by device() or a combination
      of the two (in a tuple), which is also the default.

    sample_type
      type of attack regarding with media displayed on mattescreen attacks.
      'photo' refers to a kind of attack that shows and static imagen on a screen.
      'video' refers to a attack manufactured presenting a video on a mattescreeen

    Returns: A list of :py:class:`.File` objects.
    """

    self.assert_validity()

    def check_validity(l, obj, valid, default):
      """Checks validity of user input data against a set of valid values"""
      if not l:
        return default
      elif not isinstance(l, (tuple, list)):
        return check_validity((l,), obj, valid, default)
      for k in l:
        if k not in valid:
          raise RuntimeError('Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (obj, k, valid))
      return l

    # check if groups set are valid
    VALID_GROUPS = self.groups()
    groups = check_validity(groups, "group", VALID_GROUPS, None)

    # check if supports set are valid
    VALID_SUPPORTS = self.attack_supports()
    support = check_validity(support, "support", VALID_SUPPORTS, None)

    # by default, do NOT grab enrollment data from the database
    VALID_CLASSES = ('real', 'attack', 'enroll')
    cls = check_validity(cls, "class", VALID_CLASSES, ('real', 'attack'))

    # check protocol validity
    if not protocol:
      protocol = 'grandtest'  # default
    VALID_PROTOCOLS = [k.name for k in self.protocols()]
    protocol = check_validity(protocol, "protocol", VALID_PROTOCOLS, ('grandtest',))

    # checks client identity validity
    VALID_CLIENTS = [k.id for k in self.clients()]
    clients = check_validity(clients, "client", VALID_CLIENTS, None)

    # checks if the light is valid
    VALID_LIGHTS = self.lights()
    light = check_validity(light, "light", VALID_LIGHTS, None)

    # checks if the device is valid
    VALID_DEVICES = self.devices()
    device = check_validity(device, "device", VALID_DEVICES, None)

    # checks if the device is valid
    VALID_SAMPLE_TYPE = self.attack_sample_types()
    sample_type = check_validity(sample_type, "sample_type", VALID_SAMPLE_TYPE, None)

    # now query the database
    retval = []

    # real-accesses are simpler to query
    if 'enroll' in cls:
      q = self.m_session.query(File).join(RealAccess).join(Client)
      if groups:
        q = q.filter(Client.set.in_(groups))
      if clients:
        q = q.filter(Client.id.in_(clients))
      if light:
        q = q.filter(File.light.in_(light))
      if device:
        q = q.filter(File.device.in_(device))
      q = q.filter(RealAccess.purpose == 'enroll')
      q = q.order_by(Client.id)
      retval += list(q)

    # real-accesses are simpler to query
    if 'real' in cls:
      q = self.m_session.query(File).join(RealAccess).join((Protocol, RealAccess.protocols)).join(Client)
      if groups:
        q = q.filter(Client.set.in_(groups))
      if clients:
        q = q.filter(Client.id.in_(clients))
      if light:
        q = q.filter(File.light.in_(light))
      if device:
        q = q.filter(File.device.in_(device))
      q = q.filter(Protocol.name.in_(protocol))
      q = q.order_by(Client.id)
      retval += list(q)

    # attacks will have to be filtered a little bit more
    if 'attack' in cls:
      q = self.m_session.query(File).join(Attack).join((Protocol, Attack.protocols)).join(Client)
      if groups:
        q = q.filter(Client.set.in_(groups))
      if clients:
        q = q.filter(Client.id.in_(clients))
      if support:
        q = q.filter(Attack.attack_support.in_(support))
      if sample_type:
        q = q.filter(Attack.sample_type.in_(sample_type))
      if light:
        q = q.filter(File.light.in_(light))
      if device:
        q = q.filter(File.device.in_(device))
      q = q.filter(Protocol.name.in_(protocol))
      q = q.order_by(Client.id)
      retval += list(q)

    for f in retval:
      f.original_directory = self.original_directory
      f.original_extension = self.original_extension
      f.annotation_directory = self.annotation_directory
      f.annotation_extension = self.annotation_extension
      f.annotation_type = self.annotation_type
    return retval

  def files(self, directory=None, extension=None, **object_query):
    """Returns a set of filenames for the specific query by the user.

    .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.Database.objects` instead.

    Keyword Parameters:

    directory
      A directory name that will be prepended to the final filepath returned

    extension
      A filename extension that will be appended to the final filepath returned

    object_query
      All remaining arguments are passed to :py:meth:`.Database.objects`
      untouched. Please check the documentation for such method for more
      details.

    Returns: A dictionary containing the resolved filenames considering all
    the filtering criteria. The keys of the dictionary are unique identities
    for each file in the replay attack database. Conserve these numbers if you
    wish to save processing results later on.
    """

    import warnings
    warnings.warn("The method Database.files() is deprecated, use Database.objects() for more powerful object retrieval", DeprecationWarning)

    return dict([(k.id, k.make_path(directory, extension)) for k in self.objects(**object_query)])

  def clients(self):
    """Returns an iterable with all known clients"""

    self.assert_validity()
    return list(self.m_session.query(Client))

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    self.assert_validity()
    return self.m_session.query(Client).filter(Client.id == id).count() != 0

  def protocols(self):
    """Returns all protocol objects.
    """

    self.assert_validity()
    return list(self.m_session.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""

    self.assert_validity()
    return self.m_session.query(Protocol).filter(Protocol.name == name).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    self.assert_validity()
    return self.m_session.query(Protocol).filter(Protocol.name == name).one()

  def groups(self):
    """Returns the names of all registered groups"""

    return Client.set_choices

  def lights(self):
    """Returns light variations available in the database"""

    return File.light_choices

  def devices(self):
    """Returns capture devices available in the database"""

    return File.device_choices

  def attack_supports(self):
    """Returns attack supports available in the database"""

    return Attack.attack_support_choices

  def attack_devices(self):
    """Returns attack devices available in the database"""

    return Attack.attack_device_choices

  def attack_sampling_devices(self):
    """Returns sampling devices available in the database"""

    return Attack.sample_device_choices

  def attack_sample_types(self):
    """Returns attack sample types available in the database"""

    return Attack.sample_type_choices

  def paths(self, ids, prefix='', suffix=''):
    """Returns a full file paths considering particular file ids, a given
    directory and an extension

    Keyword Parameters:

    id
      The ids of the object in the database table "file". This object should be
      a python iterable (such as a tuple or list).

    prefix
      The bit of path to be prepended to the filename stem

    suffix
      The extension determines the suffix that will be appended to the filename
      stem.

    Returns a list (that may be empty) of the fully constructed paths given the
    file ids.
    """

    self.assert_validity()

    fobj = self.m_session.query(File).filter(File.id.in_(ids))
    retval = []
    for p in ids:
      retval.extend([k.make_path(prefix, suffix) for k in fobj if k.id == p])
    return retval

  def reverse(self, paths):
    """Reverses the lookup: from certain stems, returning file ids

    Keyword Parameters:

    paths
      The filename stems I'll query for. This object should be a python
      iterable (such as a tuple or list)

    Returns a list (that may be empty).
    """

    self.assert_validity()

    fobj = self.m_session.query(File).filter(File.path.in_(paths))
    for p in paths:
      retval.extend([k.id for k in fobj if k.path == p])
    return retval

  def save_one(self, id, obj, directory, extension):
    """Saves a single object supporting the bob save() protocol.

    .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.File.save()` instead.

    This method will call save() on the the given object using the correct
    database filename stem for the given id.

    Keyword Parameters:

    id
      The id of the object in the database table "file".

    obj
      The object that needs to be saved, respecting the bob save() protocol.

    directory
      This is the base directory to which you want to save the data. The
      directory is tested for existence and created if it is not there with
      os.makedirs()

    extension
      The extension determines the way each of the arrays will be saved.
    """

    import warnings
    warnings.warn("The method Database.save_one() is deprecated, use the File object directly as returned by Database.objects() for more powerful object manipulation.", DeprecationWarning)

    self.assert_validity()

    fobj = self.m_session.query(File).filter_by(id=id).one()

    fullpath = os.path.join(directory, str(fobj.path) + extension)
    fulldir = os.path.dirname(fullpath)
    utils.makedirs_safe(fulldir)

    from bob.io.base import save

    save(obj, fullpath)

  def save(self, data, directory, extension):
    """This method takes a dictionary of blitz arrays or bob.database.Array's
    and saves the data respecting the original arrangement as returned by
    files().

    .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.File.save()` instead.

    Keyword Parameters:

    data
      A dictionary with two keys 'real' and 'attack', each containing a
      dictionary mapping file ids from the original database to an object that
      supports the bob "save()" protocol.

    directory
      This is the base directory to which you want to save the data. The
      directory is tested for existence and created if it is not there with
      os.makedirs()

    extension
      The extension determines the way each of the arrays will be saved.
    """

    import warnings
    warnings.warn("The method Database.save() is deprecated, use the File object directly as returned by Database.objects() for more powerful object manipulation.", DeprecationWarning)

    for key, value in data:
      self.save_one(key, value, directory, extension)
