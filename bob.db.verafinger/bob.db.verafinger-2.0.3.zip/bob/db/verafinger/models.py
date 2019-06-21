# vim: set fileencoding=utf-8 :


"""Table models and functionality for the VERA database.
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

  gender_choices = ('M', 'F')
  gender = Column(Enum(*gender_choices))

  age = Column(Integer)


  def __init__(self, id, gender, age):
    self.id = id
    self.gender = gender
    self.age = age


  def gender_display(self):
    """Returns a representation of the client gender"""

    return 'male' if self.gender == 'M' else 'female'


  def __repr__(self):
    return "Client(%03d) <%s>, %d years old" % \
        (self.id, self.gender_display(), self.age)



class Finger(Base):
  """Unique fingers in the database, referred by a string

  Fingers have the format ``003_L`` (i.e. <client>_<finger>)
  """

  __tablename__ = 'finger'

  id = Column(Integer, primary_key=True)

  client_id = Column(Integer, ForeignKey('client.id'))
  client = relationship("Client", backref=backref("fingers", order_by=id))

  side_choices = ('L', 'R')
  side = Column(Enum(*side_choices))

  UniqueConstraint('client_id', 'side')


  def __init__(self, client, side):
    self.client = client
    self.side = side


  @property
  def unique_name(self):
    """Unique name for this finger in the database"""

    return '%03d_%s' % (self.client.id, self.side)


  def side_display(self):
    """Returns a representation of the finger side"""

    return 'left' if self.side == 'L' else 'right'


  def __repr__(self):
    return "Finger(%03d-%s)" % (self.client.id, self.side_display())


class File(Base, bob.db.base.File):
  """Unique files in the database, referred by a string

  Files have the format ``full/bf/001-M/001_L_1`` (i.e.
  <size>/<source>/<client>-<gender>/<client>_<side>_<session>)
  """

  __tablename__ = 'file'

  id = Column(Integer, primary_key=True)

  size_choices = ('full', 'cropped')
  size = Column(Enum(*size_choices))

  source_choices = ('bf', 'pa') #bona fide or presentation attacks
  source = Column(Enum(*source_choices))

  finger_id = Column(Integer, ForeignKey('finger.id'))
  finger = relationship("Finger", backref=backref("files", order_by=id))

  session_choices = ('1', '2')
  session = Column(Enum(*session_choices))

  UniqueConstraint('size', 'source', 'finger_id', 'session')

  # this column is not really required as it can be computed from other
  # information already in the database, it is only an optimisation to allow us
  # to quickly filter files by ``model_id``
  model_id = Column(String(7))


  def __init__(self, size, source, finger, session):
    self.size = size
    self.source = source
    self.finger = finger
    self.session = session
    self.model_id = '%03d_%s_%s' % (self.finger.client.id, self.finger.side,
        self.session)


  @property
  def path(self):
    return '%s/%s/%03d-%s/%03d_%s_%s' % (self.size, self.source,
        self.finger.client.id, self.finger.client.gender,
        self.finger.client.id, self.finger.side, self.session)


  def load(self, directory=None, extension='.png'):
    """Loads the image for this file entry


    Parameters:

      directory (str): The path to the root of the dataset installation.  This
        is, *normally*, the path leading to file named ``metadata.csv`` and
        directories ``full``, ``cropped``, ``annotations`` and ``protocols``,
        but can be anything else. This behavior makes this function re-usable
        in the context of preprocessing and feature extraction, where
        intermediate files may be produced by your processing pipeline and can
        be reloaded using the same API.

      extension (str): The extension to use for loading the file in question.
        If not passed, the default ``.png`` is used.


    Returns:

      numpy.ndarray: A 2D array of unsigned integers corresponding to the input
       image for this file in (y,x) notation (Bob-style).

    """

    return bob.io.base.load(self.make_path(directory, '.png'))


  def roi(self, directory):
    """Loads region-of-interest annotations for a particular image

    The returned points (see return value below) correspond to a polygon in the
    2D space delimiting the finger image. It is up to you to generate a mask
    out of these annotations.


    Parameters:

      directory (str): The path to the root of the dataset installation.  This
        is, *forcebly*, the path leading to file named ``metadata.csv`` and
        directories ``full``, ``cropped``, ``annotations`` and ``protocols``.


    Returns:

      numpy.ndarray: A 2D array of 16-bit unsigned integers corresponding to
        annotations for the given fingervein image. Points are loaded in (y,x)
        format so, the first column of the returned array correspond to the
        y-values while the second column to the x-values of each coordinate.

    """

    directory = os.path.join(directory, 'annotations', 'roi')
    if self.size == 'full':
      return numpy.loadtxt(self.make_path(directory, '.txt'), dtype='uint16')
    else: #cropped, return the full image as RoI (150x565 pixels in yx)
      return numpy.array([[149,0], [0,0], [0,564], [149,564]], dtype='uint16')


class Protocol(Base):
  """VERA biometric recognition protocols"""

  __tablename__ = 'protocol'

  id = Column(Integer, primary_key=True)

  # Name of the protocol
  name = Column(String(10), unique=True)


  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % self.name


subset_file_association = Table('subset_file_association', Base.metadata,
  Column('file_id', Integer, ForeignKey('file.id')),
  Column('subset_id', Integer, ForeignKey('subset.id')))


class Subset(Base):
  """VERA protocol subsets"""

  __tablename__ = 'subset'

  id = Column(Integer, primary_key=True)

  protocol_id = Column(Integer, ForeignKey('protocol.id'))
  protocol = relationship("Protocol", backref=backref("subsets"))

  group_choices = ('train', 'dev')
  group = Column(Enum(*group_choices))

  purpose_choices = ('train', 'enroll', 'probe', 'attack')
  purpose = Column(Enum(*purpose_choices))

  files = relationship("File",
      secondary=subset_file_association,
      backref=backref("subsets"))


  def __init__(self, protocol, group, purpose):
    self.protocol = protocol
    self.group = group
    self.purpose = purpose


  def __repr__(self):
    return "Subset(%s, '%s', '%s')" % (self.protocol, self.group, self.purpose)


class PADProtocol(Base):
  """VERA presentation attack detection protocols"""

  __tablename__ = 'padprotocol'

  id = Column(Integer, primary_key=True)

  # Name of the protocol
  name = Column(String(10), unique=True)


  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "PADProtocol('%s')" % self.name


padsubset_file_association = Table('padsubset_file_association', Base.metadata,
  Column('file_id', Integer, ForeignKey('file.id')),
  Column('padsubset_id', Integer, ForeignKey('padsubset.id')))


class PADSubset(Base):
  """VERA protocol subsets for presentation attack detection"""

  __tablename__ = 'padsubset'

  id = Column(Integer, primary_key=True)

  protocol_id = Column(Integer, ForeignKey('padprotocol.id'))
  protocol = relationship("PADProtocol", backref=backref("padsubsets"))

  group_choices = ('train', 'dev', 'eval')
  group = Column(Enum(*group_choices))

  purpose_choices = ('real', 'attack')
  purpose = Column(Enum(*purpose_choices))

  files = relationship("File",
      secondary=padsubset_file_association,
      backref=backref("padsubsets"))


  def __init__(self, protocol, group, purpose):
    self.protocol = protocol
    self.group = group
    self.purpose = purpose


  def __repr__(self):
    return "PADSubset(%s, '%s', '%s')" % (self.protocol, self.group,
        self.purpose)
