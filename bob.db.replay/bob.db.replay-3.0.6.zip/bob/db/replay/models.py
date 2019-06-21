#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Wed 11 May 18:52:38 2011

"""Table models and functionality for the Replay Attack DB.
"""

import os
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from bob.db.base.sqlalchemy_migration import Enum, relationship
import bob.db.base
import bob.db.base.utils
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
import numpy
import bob
import bob.io.video


Base = declarative_base()


class Client(Base):
  """Database clients, marked by an integer identifier and the set they belong
  to"""

  __tablename__ = 'client'

  set_choices = ('train', 'devel', 'test')
  """Possible groups to which clients may belong to"""

  id = Column(Integer, primary_key=True)
  """Key identifier for clients"""

  set = Column(Enum(*set_choices))
  """Set to which this client belongs to"""

  def __init__(self, id, set):
    self.id = id
    self.set = set

  def __repr__(self):
    return "Client('%s', '%s')" % (self.id, self.set)


class File(Base, bob.db.base.File):
  """Generic file container"""

  __tablename__ = 'file'

  light_choices = ('controlled', 'adverse')
  """List of illumination conditions for data taking"""

  id = Column(Integer, primary_key=True)
  """Key identifier for files"""

  client_id = Column(Integer, ForeignKey('client.id'))  # for SQL
  """The client identifier to which this file is bound to"""

  path = Column(String(100), unique=True)
  """The (unique) path to this file inside the database"""

  light = Column(Enum(*light_choices))
  """The illumination condition in which the data for this file was taken"""

  # for Python
  client = relationship(Client, backref=backref('files', order_by=id))
  """A direct link to the client object that this file belongs to"""

  def __init__(self, client, path, light):
    self.client = client
    self.path = path
    self.light = light
    bob.db.base.File.__init__(path)

  def __repr__(self):
    return "File('%s')" % self.path

  def videofile(self, directory=None):
    """Returns the path to the database video file for this object

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    Returns a string containing the video file path.
    """

    return self.make_path(directory, '.mov')

  def facefile(self, directory=None):
    """Returns the path to the companion face bounding-box file

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    Returns a string containing the face file path.
    """

    if not directory:
      directory = ''
    directory = os.path.join(directory, 'face-locations')
    return self.make_path(directory, '.face')

  def bbx(self, directory=None):
    """Reads the file containing the face locations for the frames in the
    current video

    Keyword parameters:

    directory
      A directory name that will be prepended to the final filepaths where the
      face bounding boxes are located, if not on the current directory.

    Returns:
      A :py:class:`numpy.ndarray` containing information about the located
      faces in the videos. Each row of the :py:class:`numpy.ndarray`
      corresponds for one frame. The five columns of the
      :py:class:`numpy.ndarray` are (all integers):

      * Frame number (int)
      * Bounding box top-left X coordinate (int)
      * Bounding box top-left Y coordinate (int)
      * Bounding box width (int)
      * Bounding box height (int)

      Note that **not** all the frames may contain detected faces.
    """

    return numpy.loadtxt(self.facefile(directory), dtype=int)

  def is_real(self):
    """Returns True if this file belongs to a real access, False otherwise"""

    return bool(self.realaccess)

  def get_realaccess(self):
    """Returns the real-access object equivalent to this file or raise"""
    if len(self.realaccess) == 0:
      raise RuntimeError("%s is not a real-access" % self)
    return self.realaccess[0]

  def get_attack(self):
    """Returns the attack object equivalent to this file or raise"""
    if len(self.attack) == 0:
      raise RuntimeError("%s is not an attack" % self)
    return self.attack[0]

  def load(self, directory=None, extension=None):
    """Loads the data at the specified location and using the given extension.

    Keyword parameters:

    data
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory
      [optional] If not empty or None, this directory is prefixed to the final
      file destination

    extension
      [optional] The extension of the filename - this will control the type of
      output and the codec for saving the input blob.
    """
    if extension is None:
        extension = '.mov'
    vfn = self.make_path(directory, extension)

    if extension == '.mov':
        video = bob.io.video.reader(self.make_path(directory, extension))
        vin = video.load()
    else:
        vin =  bob.io.base.load(self.make_path(directory, extension))

    return vin #bob.io.base.load(self.make_path(directory, extension))


# Intermediate mapping from RealAccess's to Protocol's
realaccesses_protocols = Table('realaccesses_protocols', Base.metadata,
                               Column('realaccess_id', Integer, ForeignKey('realaccess.id')),
                               Column('protocol_id', Integer, ForeignKey('protocol.id')),
                               )

# Intermediate mapping from Attack's to Protocol's
attacks_protocols = Table('attacks_protocols', Base.metadata,
                          Column('attack_id', Integer, ForeignKey('attack.id')),
                          Column('protocol_id', Integer, ForeignKey('protocol.id')),
                          )


class Protocol(Base):
  """Replay attack protocol"""

  __tablename__ = 'protocol'

  id = Column(Integer, primary_key=True)
  """Unique identifier for the protocol (integer)"""

  name = Column(String(20), unique=True)
  """Protocol name"""

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % (self.name,)


class RealAccess(Base):
  """Defines Real-Accesses (licit attempts to authenticate)"""

  __tablename__ = 'realaccess'

  purpose_choices = ('authenticate', 'enroll')
  """Types of purpose for this video"""

  id = Column(Integer, primary_key=True)
  """Unique identifier for this real-access object"""

  file_id = Column(Integer, ForeignKey('file.id'))  # for SQL
  """The file identifier the current real-access is bound to"""

  purpose = Column(Enum(*purpose_choices))
  """The purpose of this video"""

  take = Column(Integer)
  """Take number"""

  # for Python
  file = relationship(File, backref=backref('realaccess', order_by=id))
  """A direct link to the :py:class:`.File` object this real-access belongs to"""

  protocols = relationship("Protocol", secondary=realaccesses_protocols,
                           backref='realaccesses')
  """A direct link to the protocols this file is linked to"""

  def __init__(self, file, purpose, take):
    self.file = file
    self.purpose = purpose
    self.take = take

  def __repr__(self):
    return "RealAccess('%s')" % (self.file.path)


class Attack(Base):
  """Defines Spoofing Attacks (illicit attempts to authenticate)"""

  __tablename__ = 'attack'

  attack_support_choices = ('fixed', 'hand')
  """Types of attack support"""

  attack_device_choices = ('print', 'mobile', 'highdef', 'mask')
  """Types of devices used for spoofing"""

  sample_type_choices = ('video', 'photo')
  """Original sample type"""

  sample_device_choices = ('mobile', 'highdef')
  """Original sample device"""

  id = Column(Integer, primary_key=True)
  """Unique identifier for this attack"""

  file_id = Column(Integer, ForeignKey('file.id'))  # for SQL
  """The file identifier this attack is linked to"""

  attack_support = Column(Enum(*attack_support_choices))
  """The attack support"""

  attack_device = Column(Enum(*attack_device_choices))
  """The attack device"""

  sample_type = Column(Enum(*sample_type_choices))
  """The attack sample type"""

  sample_device = Column(Enum(*sample_device_choices))
  """The attack sample device"""

  # for Python
  file = relationship(File, backref=backref('attack', order_by=id))
  """A direct link to the :py:class:`.File` object bound to this attack"""

  protocols = relationship("Protocol", secondary=attacks_protocols,
                           backref='attacks')
  """A direct link to the protocols this file is linked to"""

  def __init__(self, file, attack_support, attack_device, sample_type, sample_device):
    self.file = file
    self.attack_support = attack_support
    self.attack_device = attack_device
    self.sample_type = sample_type
    self.sample_device = sample_device

  def __repr__(self):
    return "<Attack('%s')>" % (self.file.path)
