#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


"""Table models and functionality for the UTFVP database.
"""

import os
import pkg_resources

import bob.io.base
import bob.io.image
import bob.db.base

import numpy

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean
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

  handedness_choices = ('R', 'L', 'X')
  handedness = Column(Enum(*handedness_choices))

  publishable = Column(Boolean)

  daydiff = Column(Integer)

  comment = Column(String(41))


  def __init__(self, id, gender, age, handedness, publishable, daydiff,
      comment):

    self.id = id
    self.gender = gender
    self.age = age
    self.handedness = handedness
    self.publishable = publishable
    self.daydiff = daydiff
    self.comment = comment


  def gender_display(self):
    """Returns a representation of the client gender"""

    return 'male' if self.gender == 'M' else 'female'


  def handedness_display(self):
    """Returns a representation of the client handedness"""

    return {'L': 'left', 'R': 'right', 'X': 'unknown'}[self.handedness]


  def __repr__(self):
    return "Client(%04d) <%s,%s>, %d years old" % \
        (self.id, self.gender_display(), self.handedness_display(), self.age)


class Finger(Base):
  """Unique fingers in the database, referred by a string

  Fingers have the format ``0003_3`` (i.e. <client>_<finger>)
  """

  __tablename__ = 'finger'

  id = Column(Integer, primary_key=True)

  client_id = Column(Integer, ForeignKey('client.id'))
  client = relationship("Client", backref=backref("fingers", order_by=id))

  name_choices = ('1', '2', '3', '4', '5', '6')
  name = Column(Enum(*name_choices))

  UniqueConstraint('client_id', 'name')

  # finger name enumerations relationship with human-readable versions
  finger_names = {
      '1': 'left ring',
      '2': 'left middle',
      '3': 'left index',
      '4': 'right index',
      '5': 'right middle',
      '6': 'right ring',
      }


  def __init__(self, client, name):
    self.client = client
    self.name = name


  def name_display(self):
    """Returns a representation of the finger side"""

    return Finger.finger_names[self.name]


  def __repr__(self):
    return "Finger(%04d_%s)" % (self.client.id, self.name)


class File(Base, bob.db.base.File):
  """Unique files in the database, referred by a string

  Files have the format ``0003/0003_3_2_121224-134932`` (i.e.
  ``<client>/<client>_<finger>_<session>_<date>-<hour>``)
  """

  __tablename__ = 'file'

  id = Column(Integer, primary_key=True)

  finger_id = Column(Integer, ForeignKey('finger.id'))
  finger = relationship("Finger", backref=backref("files", order_by=id))

  session_choices = ('1', '2', '3', '4')
  session = Column(Enum(*session_choices))

  UniqueConstraint('finger_id', 'session')

  # this column is not really required as it can be computed from other
  # information already in the database, it is only an optimisation to allow us
  # to quickly filter files by ``model_id``
  model_id = Column(String(8), unique=True)

  # we don't use this, but store to retrieve filename from table row
  date_hour = Column(String(13))


  def __init__(self, finger, session, date_hour):
    self.finger = finger
    self.session = session
    self.model_id = '%04d_%s_%s' % (self.finger.client.id, self.finger.name,
        self.session)
    self.date_hour = date_hour


  @property
  def path(self):
    return '%04d/%04d_%s_%s_%s' % (self.finger.client.id,
        self.finger.client.id, self.finger.name, self.session, self.date_hour)


  def __repr__(self):
    return "<File('%s')>" % self.path


  @property
  def unique_finger_name(self):
    """Unique name for a given finger in the database"""

    return '%04d_%s' % (self.finger.client.id, self.finger.name)


  def load(self, directory=None, extension='.png'):
    """Loads the image for this file entry


    Parameters:

      directory (str): The path to the root of the database installation.  This
        is the path leading to files named ``DDD-G`` where ``D``'s correspond
        to digits and ``G`` to the client gender. For example ``032-M``.


    Returns:

      numpy.ndarray: A 2D array of unsigned integers corresponding to the input
       image for this file in (y,x) notation (Bob-style).

    """

    return bob.io.base.load(self.make_path(directory, '.png'))


  def roi(self):
    """Loads region-of-interest annotations for a particular image

    The returned points (see return value below) correspond to a polygon in the
    2D space delimiting the finger image. It is up to you to generate a mask
    out of these annotations.


    Returns:

      numpy.ndarray: A 2D array of 16-bit unsigned integers corresponding to
        annotations for the given fingervein image. Points are loaded in (y,x)
        format so, the first column of the returned array correspond to the
        y-values while the second column to the x-values of each coordinate.

    """

    # calculate where the annotations for this file are
    directory = pkg_resources.resource_filename(__name__,
        os.path.join('data', 'annotations', 'roi'))

    # loads it w/o mercy ;-)
    return numpy.loadtxt(self.make_path(directory, '.txt'), dtype='uint16')



class Protocol(Base):
  """VERA protocols"""

  __tablename__ = 'protocol'

  id = Column(Integer, primary_key=True)

  # Name of the protocol
  name = Column(String(15), unique=True)


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

  group_choices = ('train', 'dev', 'eval')
  group = Column(Enum(*group_choices))

  purpose_choices = ('train', 'enroll', 'probe')
  purpose = Column(Enum(*purpose_choices))

  files = relationship("File",
      secondary=subset_file_association,
      backref=backref("subsets"))

  avoid_self_probe = Column(Boolean, default=False)


  def __init__(self, protocol, group, purpose):
    self.protocol = protocol
    self.group = group
    self.purpose = purpose


  def __repr__(self):
    return "Subset(%s, %s, %s)" % (self.protocol, self.group, self.purpose)
