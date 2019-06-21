#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Table models and functionality for the 3d mask attack database
"""

import os
from sqlalchemy import Table, Column, Integer, String, ForeignKey, or_, and_, not_
from bob.db.base.sqlalchemy_migration import Enum, relationship
import bob.db.base.utils
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
import bob.io.video
from bob.db.base import File as BaseFile
import bob.core

Base = declarative_base()

#protocolPurpose_file_association_fix = Table('protocolPurpose_file_association_fix', Base.metadata,
#  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
#  Column('file_id', Integer, ForeignKey('file.id')))
protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('file_id', Integer, ForeignKey('file.id')))

class Client(Base):
  """Database clients, marked by an integer identifier and the set they belong to"""

  __tablename__ = 'client'

  set_choices = ('world', 'dev', 'test')
  """Possible groups to which clients may belong to"""

  id = Column(Integer, primary_key=True)
  """Key identifier for clients"""

  set = Column(Enum(*set_choices))
  """Set to which this client belongs to"""
  
  #fixset = Column(Enum(*set_choices))
  """Set to which this client belongs to"""

  def __init__(self, client_id, dataset):
    self.id = client_id
    self.set = dataset

  def __repr__(self):
    return "Client('%s', '%s'')" % (self.id, self.set)

class File(Base, BaseFile):
  """Generic file container"""

  __tablename__ = 'file'

  #session_choices = (1, 2)
  """List of sessions """

  #shot_choices = (1, 2, 3, 4, 5)
  """List of shots """

  id = Column(Integer, primary_key=True)
  """Key identifier for files"""

  client_id = Column(Integer, ForeignKey('client.id')) # for SQL
  """The client identifier to which this file is bound to"""

  path = Column(String(100), unique=True)
  """The (unique) path to this file inside the database"""

  session = Column(Integer)
  """The session identifier in which the data for this file was taken"""

  shot = Column(Integer)
  """The shot identifier in which the data for this file was taken"""

  # for Python
  client = relationship(Client, backref=backref('files', order_by=id))
  """A direct link to the client object that this file belongs to"""

  def __init__(self, client_id, path, session, shot):
    self.client_id = client_id
    self.path = path
    self.session = session
    self.shot = shot

  def is_real(self):
    if self.session == 3:
      return False
    else:
      return True

  def videofile(self, directory=None):
    """Returns the path to the database video file for this object
    Keyword parameters:
    directory: An optional directory name that will be prefixed to the returned result.

    Returns a string containing the video file path.
    """
    return self.make_path(directory, '.avi')

  def facefile(self, directory=''):
    return self.make_path(directory, '.face')

  def eyes(self, directory=None):
    coords = numpy.loadtxt(self.facefile(directory), delimiter=',')

  def __repr__(self):
    return "File('%s')" % self.path

  def make_path(self, directory=None, extension='.hdf5'):
    """Wraps the current path so that a complete path is formed

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.jpg`` or
      ``.hdf5``.

    Returns a string containing the newly generated file path.
    """

    if not directory: directory = ''
    if not extension: extension = ''

    return str(os.path.join(directory, self.path + extension))

  def load(self, directory=None, extension='.hdf5', isdepth=True, iseye=True):
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
    f =  bob.io.base.HDF5File(self.make_path(directory, extension))    
    color_image = f.read('Color_Data')
    if isdepth:
        depth_image = f.read('Depth_Data')
    if iseye:
        eye_pos = f.read('Eye_Pos')
    del f
    if isdepth and iseye:
        return (color_image, depth_image, eye_pos)
    elif isdepth:
        return (color_image, depth_image)
    elif iseye:
        return (color_image, eye_pos)
    else:
        return color_image

  def save(self, data, directory=None, extension='.hdf5'):
    """Saves the input data at the specified location and using the given
    extension.

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

    path = self.make_path(directory, extension)
    bob.db.utils.makedirs_safe(os.path.dirname(path))
    bob.io.save(data, path)

class Protocol(Base):
  """Mask attack protocol"""

  __tablename__ = 'protocol'

  id = Column(Integer, primary_key=True)
  """Unique identifier for the protocol (integer)"""

  name = Column(String(20), unique=True)
  """Protocol name"""

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % (self.name,)

class ProtocolPurpose(Base):
  """Biosecure protocol purposes"""

  __tablename__ = 'protocolPurpose'

  id = Column(Integer, primary_key=True)
  """Unique identifier for this protocol purpose (integer)"""
  
  protocol_id = Column(Integer, ForeignKey('protocol.id')) # for SQL
  """Id of the protocol associated with this protocol purpose"""
  
  set_choices = ('world', 'dev', 'test')
  set = Column(Enum(*set_choices))
  """Group associated with this protocol purpose"""
  
  purpose_choices = ('trainReal', 'trainMask', 'enrol', 'probeReal', 'probeMask', 'classifyReal', 'classifyMask')
  purpose = Column(Enum(*purpose_choices))
  """Purpose associated with this protocol purpose"""
  
  session_list = Column(String(10))

  protocol = relationship("Protocol", backref=backref("purposes", order_by=id))
  """A direct link to the Protocol object that this protocol purpose belongs to"""
  
  #fixfiles = relationship("File", secondary=protocolPurpose_file_association_fix, backref=backref("fixprotocolPurposes", order_by=id))
  files = relationship("File", secondary=protocolPurpose_file_association, backref=backref("protocolPurposes", order_by=id))
  """Direct links to the File objects associated with this protocol purpose"""

  def __init__(self, protocol_id, set, purpose, sessionlist):
    self.protocol_id = protocol_id
    self.set = set
    self.purpose = purpose
    self.session_list = sessionlist

  def __repr__(self):
    return "ProtocolPurpose('%s', '%s', '%s')" % (self.protocol.name, self.set, self.purpose)

