#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base

import bob.core

logger = bob.core.log.setup('bob.db.fargo')
Base = declarative_base()

# association table between File and ProtocolPurpose
protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('file_id',  Integer, ForeignKey('file.id')))

class Client(Base):
  """Database clients.
  
  Clients are marked by an integer identifier and the set they belong to.
  
  Attributes
  ----------
  id: int
    The client (subject) id.
  group: str
    The group this client belongs to (either 'world', 'dev' or 'eval')
  
  """
  
  __tablename__ = 'client'
  id = Column(Integer, primary_key=True)
  group_choices = ('world', 'dev', 'eval')
  group = Column(Enum(*group_choices))

  def __init__(self, id, group):
    """ Init function
    
    Parameters
    ----------
    id: int
      The client (subject) id.
    group: str
      The group this client belongs to (either 'world', 'dev' or 'eval')
    
    """
    self.id = id
    self.group = group

  def __repr__(self):
    return "Client('%s', '%s')" % (self.id, self.group)


class File(Base, bob.db.base.File):
  """Generic file container
  
  Class that defines an image file of the FARGO database.

  Attributes
  ----------
  client_id: int
    The id of the client associated to this file
  light: str
    The light condition of the image
  device: str
    The device with which this file was acquired
  recording: str
    The recording from which this file originated
  modalitiy: str
    The modality from which this file was recorded
  pose: str
    The pose of the face in the image
  path: str
    The path on the disk where this file is stored.
  
  """

  __tablename__ = 'file'

  # key id for files
  id = Column(Integer, primary_key=True)

  # client id of this file
  client_id = Column(Integer, ForeignKey('client.id'))  
  client = relationship(Client, backref=backref('files', order_by=id))

  # illumination conditions
  light_choices = ('controlled', 'dark', 'outdoor')
  light = Column(Enum(*light_choices))

  # mounted devices
  device_choices = ('laptop', 'mobile')
  device = Column(Enum(*device_choices))
  
  # recordings
  recording_choices = ('0', '1')
  recording = Column(Enum(*recording_choices))

  # modality
  modality_choices = ('rgb', 'nir', 'depth')
  modality = Column(Enum(*modality_choices))

  # pose
  pose_choices = ('frontal', 'yaw', 'pitch')
  pose = Column(Enum(*pose_choices))

  # path of this file in the database
  path = Column(String(100), unique=True)

  def __init__(self, client_id, path, light, device, pose, modality, recording):
    """ Init function

    Parameters
    ----------
    client_id: int
      The id of the client associated to this file
    path: str
      The path on the disk where this file is stored.
    light: str
      The light condition of the image
    device: str
      The device with which this file was acquired
    pose: str
      The pose of the face in the image
    modalitiy: str
      The modality from which this file was recorded
    recording: str
      The recording from which this file originated
    
    """
    bob.db.base.File.__init__(self, path=path)
    self.client_id = client_id
    self.light = light
    self.device = device
    self.recording = recording
    self.modality = modality
    self.pose = pose


  def __repr__(self):
    return "File('%s')" % self.path


  def make_path(self, directory=None, extension=None):
    """Wraps the current path so that a complete path is formed

    Parameters
    ----------
    directory
      An optional directory name that will be prefixed to the returned result.
    extension
      An optional extension that will be suffixed to the returned filename. 
      extension normally includes the leading ``.`` character 

    Returns
    -------
    str:
      the newly generated file path.
    
    """
    if not directory:
      directory = ''
    if not extension:
      extension = ''
    return str(os.path.join(directory, self.path + extension))


class Protocol(Base):
  """FARGO protocols
 
  The class representing the protocols

  Attributes
  ----------
  name:
    The name of the protocol
  """

  __tablename__ = 'protocol'

  id = Column(Integer, primary_key=True)
  name = Column(String(20), unique=True)

  def __init__(self, name):
    """ Init function

    Parameters
    ----------
    name:
      The name of the protocol
    
    """
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % (self.name,)


class ProtocolPurpose(Base):
  """FARGO protocol purposes
  
  This class represent the protocol purposes, and 
  more importantly, contains the set of files
  associated with each group and each purpose
  for each protocol.

  Attributes
  ----------
  protocol_id: str
    The associated protocol
  group: str
    The group in the associated protocol ('world', 'dev' or 'eval')
  purpose: str
    The purpose of the group in this protocol ('train', 'enroll' or 'probe')
  
  """

  __tablename__ = 'protocolPurpose'

  id = Column(Integer, primary_key=True)
  
  protocol_id = Column(Integer, ForeignKey('protocol.id'))
  group_choices = ('world', 'dev', 'eval')
  group = Column(Enum(*group_choices))
  purpose_choices = ('train', 'enroll', 'probe')
  purpose = Column(Enum(*purpose_choices))

  # protocol: a protocol have 1 to many purpose
  protocol = relationship("Protocol", backref=backref("purposes", order_by=id))
  
  # files: many to many relationship
  files = relationship("File", secondary=protocolPurpose_file_association, backref=backref("protocolPurposes", order_by=id))

  def __init__(self, protocol_id, group, purpose):
    """ Init function

    Parameters
    ----------
    protocol_id: str
      The associated protocol
    group: str
      The group in the associated protocol ('world', 'dev' or 'eval')
    purpose: str
      The purpose of the group in this protocol ('train', 'enroll' or 'probe')
   
    """
    self.protocol_id = protocol_id
    self.group = group
    self.purpose = purpose

  def __repr__(self):
    return "ProtocolPurpose('%s', '%s', '%s')" % (self.protocol.name, self.group, self.purpose)


