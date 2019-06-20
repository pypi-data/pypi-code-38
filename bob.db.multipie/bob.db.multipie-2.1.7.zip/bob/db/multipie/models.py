#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Table models and functionality for the Multi-PIE database.
"""

import os, numpy
import bob.db.base.utils
from sqlalchemy import Table, Column, Integer, String, ForeignKey, or_, and_, not_
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base


Base = declarative_base()

subworld_client_association = Table('subworld_client_association', Base.metadata,
  Column('subworld_id', Integer, ForeignKey('subworld.id')),
  Column('client_id',  Integer, ForeignKey('client.id')))

protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('file_id',  Integer, ForeignKey('file.id')))

class Client(Base):
  """Database clients, marked by an integer identifier and the group they belong to"""

  __tablename__ = 'client'

  # Key identifier for the client
  id = Column(Integer, primary_key=True)
  # Group to which the client belongs to
  group_choices = ('dev', 'eval', 'world')
  sgroup = Column(Enum(*group_choices))
  # Birthyear of the client
  birthyear = Column(Integer)
  # Gender to which the client belongs to
  gender_choices = ('male','female')
  gender = Column(Enum(*gender_choices))
  first_session = Column(Integer)
  second_session = Column(Integer)
  third_session = Column(Integer)
  fourth_session = Column(Integer)

  def __init__(self, id, group, birthyear, gender, first_session, second_session, third_session, fourth_session):
    self.id = id
    self.sgroup = group
    self.birthyear = birthyear
    self.gender = gender
    self.first_session = first_session
    self.second_session = second_session
    self.third_session = third_session
    self.fourth_session = fourth_session

  def __repr__(self):
    return "Client(%d, '%s')" % (self.id, self.sgroup)

class Subworld(Base):
  """Database clients belonging to the world group are split in two disjoint subworlds,
     onethird and twothirds"""

  __tablename__ = 'subworld'

  # Key identifier for this Subworld object
  id = Column(Integer, primary_key=True)
  # Subworld to which the client belongs to
  name = Column(String(20), unique=True)

  # for Python: A direct link to the client
  clients = relationship("Client", secondary=subworld_client_association, backref=backref("subworld", order_by=id))

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Subworld('%s')" % (self.name)

class File(Base, bob.db.base.File):
  """Generic file container"""

  __tablename__ = 'file'

  # Key identifier for the file
  id = Column(Integer, primary_key=True)
  # Key identifier of the client associated with this file
  client_id = Column(Integer, ForeignKey('client.id')) # for SQL
  # Unique path to this file inside the database
  path = Column(String(100), unique=True)
  # Identifier of the session
  session_id = Column(Integer)
  # Identifier of the recording
  recording_id = Column(Integer)
  # Image type
  imagetype_choices = ('multiview', 'highres')
  img_type = Column(Enum(*imagetype_choices))
  # Identifier of the expression
  expression_id = Column(Integer, ForeignKey('expression.id'))

  # for Python
  client = relationship("Client", backref=backref("files", order_by=id))

  def __init__(self, client_id, path, session_id, recording_id, img_type, expression_id):
    # call base class constructor
    bob.db.base.File.__init__(self, path = path)
    self.client_id = client_id

    self.session_id = session_id
    self.recording_id = recording_id
    self.img_type = img_type
    self.expression_id = expression_id

class FileMultiview(Base):
  """Additional file information for multiview-like files"""

  __tablename__ = 'fileMultiview'

  # Key identifier for the file multiview
  id = Column(Integer, ForeignKey('file.id'), primary_key=True) # for SQL
  # Identifier of the shot
  shot_id = Column(Integer)
  # Identifier of the camera
  camera_id = Column(Integer, ForeignKey('camera.id'))

  # for Python
  file = relationship("File", uselist=False, backref=backref("file_multiview", uselist=False, order_by=id))

  def __init__(self, file_id, shot_id, camera_id):
    self.id = file_id
    self.shot_id = shot_id
    self.camera_id = camera_id

  def __repr__(self):
    return "FileMultiview('%s')" % (self.file.path)

class Expression(Base):
  """Multi-PIE expressions"""

  __tablename__ = 'expression'

  id = Column(Integer, primary_key=True)
  name = Column(String(20), unique=True)

  # for Python: A direct link to the files with this expression
  files = relationship("File", backref=backref("expression", order_by=id))

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Expression('%s')" % (self.name)

class Camera(Base):
  """Multi-PIE cameras"""

  __tablename__ = 'camera'

  id = Column(Integer, primary_key=True)
  name = Column(String(10), unique=True)

  # for Python: A direct link to the files (multiview) recorded with this camera
  files_multiview = relationship("FileMultiview", backref=backref("camera", order_by=id))

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Camera('%s')" % (self.name)

class Protocol(Base):
  """Multi-PIE protocols"""

  __tablename__ = 'protocol'

  # Unique identifier for this protocol object
  id = Column(Integer, primary_key=True)
  # Name of the protocol associated with this object
  name = Column(String(20), unique=True)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % (self.name,)

class ProtocolPurpose(Base):
  """Multi-PIE protocol purposes"""

  __tablename__ = 'protocolPurpose'

  # Unique identifier for this protocol purpose object
  id = Column(Integer, primary_key=True)
  # Id of the protocol associated with this protocol purpose object
  protocol_id = Column(Integer, ForeignKey('protocol.id')) # for SQL
  # Group associated with this protocol purpose object
  group_choices = Client.group_choices
  sgroup = Column(Enum(*group_choices))
  # Purpose associated with this protocol purpose object
  purpose_choices = ('train', 'enroll', 'probe')
  purpose = Column(Enum(*purpose_choices))

  # For Python: A direct link to the Protocol object that this ProtocolPurpose belongs to
  protocol = relationship("Protocol", backref=backref("purposes", order_by=id))
  # For Python: A direct link to the File objects associated with this ProtcolPurpose
  files = relationship("File", secondary=protocolPurpose_file_association, backref=backref("protocol_purposes", order_by=id))

  def __init__(self, protocol_id, sgroup, purpose):
    self.protocol_id = protocol_id
    self.sgroup = sgroup
    self.purpose = purpose

  def __repr__(self):
    return "ProtocolPurpose('%s', '%s', '%s')" % (self.protocol.name, self.sgroup, self.purpose)

