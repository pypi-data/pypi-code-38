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

"""Table models and functionality for the SCFace database.
"""

import bob.db.base.utils
from sqlalchemy import Table, Column, Integer, Boolean, String, ForeignKey, or_, and_, not_
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
  group_choices = ('dev','eval','world')
  sgroup = Column(Enum(*group_choices)) # do NOT use group (SQL keyword)
  # Birthyear of the client
  birthyear = Column(Integer)
  # Gender to which the client belongs to
  gender_choices = ('m','f')
  gender = Column(Enum(*gender_choices))
  # Does he has a beard?
  beard = Column(Boolean)
  # Does he has a moustache?
  moustache = Column(Boolean)
  # Does he has glasses?
  glasses = Column(Boolean)

  def __init__(self, id, group, birthyear, gender, beard, moustache, glasses):
    self.id = id
    self.sgroup = group
    self.birthyear = birthyear
    self.gender = gender
    self.beard = beard
    self.moustache = moustache
    self.glasses = glasses

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
  # Camera identifier
  camera = Column(String(8))
  # Distance identifier
  distance = Column(Integer)

  # For Python: A direct link to the client object that this file belongs to
  client = relationship("Client", backref=backref("files", order_by=id))
  annotation = relationship("Annotation", backref=backref("file", order_by=id, uselist=False), uselist=False)

  def __init__(self, client_id, path, camera, distance):
    # call base class constructor
    bob.db.base.File.__init__(self, path = path)
    self.client_id = client_id
    # set the remaining information of the file
    self.camera = camera
    self.distance = distance
    self.client_id = client_id

class Annotation(Base):
  """Annotations of the SC face database consists of the left and right eye positions as well as the nose tip and the center of the mouth.
  There is exactly one annotation for each file."""
  __tablename__ = 'annotation'

  id = Column(Integer, primary_key=True)
  file_id = Column(Integer, ForeignKey('file.id'))

  le_x = Column(Integer) # left eye
  le_y = Column(Integer)
  re_x = Column(Integer) # right eye
  re_y = Column(Integer)
  n_x = Column(Integer) # nose tip
  n_y = Column(Integer)
  m_x = Column(Integer) # mouth center
  m_y = Column(Integer)

  def __init__(self, file_id, annotations):
    self.file_id = file_id

    assert len(annotations) == 8
    self.re_x = int(annotations[0])
    self.re_y = int(annotations[1])
    self.le_x = int(annotations[2])
    self.le_y = int(annotations[3])
    self.n_x = int(annotations[4])
    self.n_y = int(annotations[5])
    self.m_x = int(annotations[6])
    self.m_y = int(annotations[7])

  def __call__(self):
    """Returns the annotations of this database in a dictionary: {'reye' : (re_y, re_x), 'leye' : (le_y, le_x)}."""
    return {'reye' : (self.re_y, self.re_x), 'leye' : (self.le_y, self.le_x), 'nose' : (self.n_y, self.n_x), 'mouth' : (self.m_y, self.m_x) }

  def __repr__(self):
    return "<Annotation('%s': 'reye'=%dx%d, 'leye'=%dx%d, 'nose'=%dx%d, 'mouth'=%dx%d)>" % (self.file_id, self.re_y, self.re_x, self.le_y, self.le_x,self.n_y, self.n_x, self.m_y, self.m_x)


class Protocol(Base):
  """SCface protocols"""

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
  """SCface protocol purposes"""

  __tablename__ = 'protocolPurpose'

  # Unique identifier for this protocol purpose object
  id = Column(Integer, primary_key=True)
  # Id of the protocol associated with this protocol purpose object
  protocol_id = Column(Integer, ForeignKey('protocol.id')) # for SQL
  # Group associated with this protocol purpose object
  group_choices = ('world', 'dev', 'eval')
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
