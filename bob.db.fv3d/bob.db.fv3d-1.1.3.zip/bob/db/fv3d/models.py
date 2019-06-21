#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


"""Table models and functionality for the 3D Fingervein database.
"""

import os
import pkg_resources

import bob.io.base
import bob.io.image
import bob.db.base

import numpy

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy import or_, and_, not_
from sqlalchemy import UniqueConstraint

from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Client(Base):
  """Unique clients in the database, referred by a single integer"""

  __tablename__ = 'client'

  id = Column(Integer, primary_key=True)

  age = Column(Integer)

  gender_choices = ('m', 'f')
  gender = Column(Enum(*gender_choices))

  skin_color_choices = tuple([str(k) for k in range(1,7)] + ['x'])
  skin_color = Column(Enum(*skin_color_choices))

  occupation_choices = tuple([str(k) for k in range(10)] + ['x'])
  occupation = Column(Enum(*occupation_choices))


  def __init__(self, id, gender, age, skin_color, occupation):
    self.id = id
    self.gender = gender
    self.age = age
    self.skin_color = skin_color
    self.occupation = occupation


  def gender_display(self):
    """Returns a representation of the client gender"""

    return 'male' if self.gender == 'm' else 'female'


  def skin_color_display(self):
    """Returns a representation of the client skin color"""

    mapping = {
        'x': 'unknown',
        '1': 'I', #celtic
        '2': 'II', #scandinavian
        '3': 'III', #caucasian
        '4': 'IV', #mediterranean, hispanic and some asian
        '5': 'V', # pakistani and indian
        '6': 'VI', # african
        }

    return mapping[self.skin_color]


  def occupation_display(self):
    """Returns a representation of the client occupation"""

    mapping = {
      'x': 'unknown',
      '0': '0-armed forces',
      '1': '1-manager',
      '2': '2-professional',
      '3': '3-technician',
      '4': '4-cleric',
      '5': '5-sales',
      '6': '6-agricultural',
      '7': '7-craft',
      '8': '8-machines',
      '9': '9-elementary',
      }

    return mapping[self.occupation]


  def __repr__(self):
    return "Client(%03d) <%s>, %d years old, %s, %s" % \
        (self.id, self.gender_display(), self.age, self.skin_color_display(),
            self.occupation_display())



class Finger(Base):
  """Unique fingers in the database, referred by a string

  Fingers have the format ``003_L`` (i.e. <client>_<finger>)
  """

  __tablename__ = 'finger'

  id = Column(Integer, primary_key=True)

  client_id = Column(Integer, ForeignKey('client.id'))
  client = relationship("Client", backref=backref("fingers", order_by=id))

  side_choices = ('l', 'r')
  side = Column(Enum(*side_choices))

  name_choices = ('t', 'i', 'm', 'r', 'l')
  name = Column(Enum(*name_choices))

  UniqueConstraint('client_id', 'side', 'name')


  def __init__(self, client, side, name):
    self.client = client
    self.side = side
    self.name = name


  def side_display(self):
    """Returns a representation of the finger side"""

    mapping = {
        'l': 'left',
        'r': 'right',
        }

    return mapping[self.side]


  def name_display(self):
    """Returns a representation of the finger name"""

    mapping = {
        't': 'thumb',
        'i': 'index',
        'm': 'middle',
        'r': 'ring',
        'l': 'little',
        }

    return mapping[self.name]


  def __repr__(self):
    return "Finger(%03d, %s, %s)" % (self.client.id, self.side_display(),
        self.name_display())


  @property
  def unique_name(self):
    """Unique name for a given finger in the database"""

    return '{id:03}-{side}{finger}'.format(id=self.client.id,
        side=self.side, finger=self.name)



class File(Base, bob.db.base.File):
  """Unique files in the database, referred by a string

  Filenames inside the 3D Fingervein are like these:

  <client>/<session>/<attempt>/<client>-<age>-<gender><skin><occ><side><finger><session><attempt><snap><cam>.png

  The fields can have these values:

    * client: integer > 0
    * age = integer > 0
    * gender = str, 'm' or 'f'
    * skin (color) = str, '1'..'6' or 'x'
    * occ(upation) = str, '0'..'9' or 'x'
    * side = str, 'l' or 'r'
    * finger = str, 't', 'i', 'm', 'r', 'l'
    * session = int > 0
    * attempt = int > 0
    * snap = int > 0
    * cam = str, one of '1', '2', '3' or 'S' ('stitched')

  """

  __tablename__ = 'file'

  id = Column(Integer, primary_key=True)

  finger_id = Column(Integer, ForeignKey('finger.id'))
  finger = relationship("Finger", backref=backref("files", order_by=id))

  session_choices = ('1', '2', '3')
  session = Column(Enum(*session_choices))

  attempt_choices = ('1', '2')
  attempt = Column(Enum(*attempt_choices))

  snapshot_choices = ('1', '2', '3', '4', '5')
  snapshot = Column(Enum(*snapshot_choices))

  camera_choices = ('1', '2', '3', 'S')
  camera = Column(Enum(*camera_choices))

  UniqueConstraint('finger_id', 'session', 'attempt', 'snapshot', 'camera')


  def __init__(self, finger, session, attempt, snapshot, camera):
    self.finger = finger
    self.session = session
    self.attempt = attempt
    self.snapshot = snapshot
    self.camera = camera


  @property
  def path(self):

    fmt = '{id:03}/{session}/{attempt}/{id:03}-{age:03}-{gender}{skin}{occ}{side}{finger}{session}{attempt}{snap}{cam}'
    info = {
        'id': self.finger.client.id,
        'age': self.finger.client.age,
        'gender': self.finger.client.gender,
        'skin': self.finger.client.skin_color,
        'occ': self.finger.client.occupation,
        'side': self.finger.side,
        'finger': self.finger.name,
        'session': self.session,
        'attempt': self.attempt,
        'snap': self.snapshot,
        'cam': self.camera,
        }
    return fmt.format(**info)


  def load(self, directory=None, extension='.png'):
    """Loads the image for this file entry


    Parameters:

      directory (str): The path to the root of the database installation.  This
        is the path leading to directories named ``DDD`` where ``D``'s
        correspond to digits.


    Returns:

      numpy.ndarray: A 2D array of unsigned integers corresponding to the input
       image for this file in (y,x) notation (Bob-style).

    """

    return bob.io.base.load(self.make_path(directory, extension))


  def has_roi(self):
    """Tells if the RoI for a sample is available


    Returns:

      bool: ``True`` if this sample has an RoI

    """

    # calculate where the annotations for this file are
    directory = pkg_resources.resource_filename(__name__,
        os.path.join('data', 'annotations', 'roi'))

    return os.path.exists(self.make_path(directory, '.txt'))


  def roi(self):
    """Loads region-of-interest annotations for a particular image

    The returned points (see return value below) correspond to a polygon in the
    2D space delimiting the finger image. It is up to you to generate a mask
    out of these annotations.


    Returns:

      numpy.ndarray: A 2D array of 8-bit unsigned integers corresponding to
        annotations for the given fingervein image. Points are loaded in (y,x)
        format so, the first column of the returned array correspond to the
        y-values while the second column to the x-values of each coordinate.

    """

    # calculate where the annotations for this file are
    directory = pkg_resources.resource_filename(__name__,
        os.path.join('data', 'annotations', 'roi'))

    # loads it w/o mercy ;-)
    return numpy.loadtxt(self.make_path(directory, '.txt'), dtype='uint16')



train_file_association = Table('train_file_association', Base.metadata,
  Column('protocol_id', Integer, ForeignKey('protocol.id')),
  Column('file_id', Integer, ForeignKey('file.id')))

class Protocol(Base):
  """3D Fingervein protocols"""

  __tablename__ = 'protocol'

  id = Column(Integer, primary_key=True)

  # Name of the protocol
  name = Column(String(10), unique=True)

  training_set = relationship("File",
      secondary=train_file_association,
      backref=backref("train_subsets"))


  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % self.name


model_file_association = Table('model_file_association', Base.metadata,
  Column('model_id', Integer, ForeignKey('model.id')),
  Column('file_id', Integer, ForeignKey('file.id')))

class Model(Base):
  """Unique models in the database, referred by a string and associate to a
  protocol
  """

  __tablename__ = 'model'

  id = Column(Integer, primary_key=True)

  # Name of the model
  name = Column(String(9))

  # Group of this model
  group_choices = ('dev', 'eval')
  group = Column(Enum(*group_choices))

  # The finger it models
  finger_id = Column(Integer, ForeignKey('finger.id'))
  finger = relationship("Finger", backref=backref("models", order_by=id))

  # Which files to use for the said finger. All files should belong to the same
  # finger
  files = relationship("File",
      secondary=model_file_association,
      backref=backref("models"))

  # To which protocol is this model associated to?
  protocol_id = Column(Integer, ForeignKey('protocol.id'))
  protocol = relationship("Protocol", backref=backref("models", order_by=id))

  UniqueConstraint('name', 'protocol', name='name_protocol')


  def __init__(self, name, group, finger, protocol):
    self.name = name
    self.group = group
    self.finger = finger
    self.protocol = protocol

  def __repr__(self):
    return "Model(%s, %s, %s, %s)" % (self.name, self.group, self.finger,
        self.protocol)


class Probe(Base):
  """Unique probes in the database associated to a protocol and a single file
  """

  __tablename__ = 'probe'

  id = Column(Integer, primary_key=True)

  # Group of this probe
  group_choices = Model.group_choices
  group = Column(Enum(*group_choices))

  # To which protocol is this probe associated to?
  protocol_id = Column(Integer, ForeignKey('protocol.id'))
  protocol = relationship("Protocol", backref=backref("probes", order_by=id))

  # To which file is this probe associated to?
  file_id = Column(Integer, ForeignKey('file.id'))
  file = relationship("File", backref=backref("probes", order_by=id))


  def __init__(self, group, protocol, file):
    self.group = group
    self.protocol = protocol
    self.file = file

  def __repr__(self):
    return "Probe(%s, %s, %s)" % (self.group, self.protocol, self.file)
