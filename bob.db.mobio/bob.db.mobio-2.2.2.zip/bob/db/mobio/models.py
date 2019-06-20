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

"""Table models and functionality for the Mobio database.
"""

import bob.db.base.utils
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base

Base = declarative_base()

subworld_client_association = Table('subworld_client_association', Base.metadata,
                                    Column('subworld_id', Integer, ForeignKey('subworld.id')),
                                    Column('client_id', Integer, ForeignKey('client.id')))

subworld_file_association = Table('subworld_file_association', Base.metadata,
                                  Column('subworld_id', Integer, ForeignKey('subworld.id')),
                                  Column('file_id', Integer, ForeignKey('file.id')))

tmodel_file_association = Table('tmodel_file_association', Base.metadata,
                                Column('tmodel_id', String, ForeignKey('tmodel.id')),
                                Column('file_id', Integer, ForeignKey('file.id')))

protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
                                         Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
                                         Column('file_id', Integer, ForeignKey('file.id')))


class Client(Base):
  """Database clients, marked by an integer identifier and the group they belong to"""

  __tablename__ = 'client'

  # Key identifier for the client
  id = Column(Integer, primary_key=True)
  # Gender to which the client belongs to
  gender_choices = ('female', 'male')
  gender = Column(Enum(*gender_choices))
  # Group to which the client belongs to
  group_choices = ('dev', 'eval', 'world')
  sgroup = Column(Enum(*group_choices))  # do NOT use group (SQL keyword)
  # Institute to which the client belongs to
  institute_choices = ('idiap', 'manchester', 'surrey', 'oulu', 'brno', 'avignon')
  institute = Column(Enum(*institute_choices))

  def __init__(self, id, group, gender, institute):
    self.id = id
    self.sgroup = group
    self.gender = gender
    self.institute = institute

  def __repr__(self):
    return "Client('%d', '%s')" % (self.id, self.sgroup)


class Subworld(Base):
  """Database clients belonging to the world group are split in subsets"""

  __tablename__ = 'subworld'

  # Key identifier for this Subworld object
  id = Column(Integer, primary_key=True)
  # Subworld to which the client belongs to
  name = Column(String(20), unique=True)

  # for Python: A direct link to the client
  clients = relationship("Client", secondary=subworld_client_association, backref=backref("subworld", order_by=id))
  # for Python: A direct link to the files
  files = relationship("File", secondary=subworld_file_association, backref=backref("subworld", order_by=id))

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Subworld('%s')" % (self.name)


class TModel(Base):
  """T-Norm models"""

  __tablename__ = 'tmodel'

  # Unique identifier for this TModel object
  id = Column(Integer, primary_key=True)
  # Model id (only unique for a given protocol)
  mid = Column(String(9))
  client_id = Column(Integer, ForeignKey('client.id'))  # for SQL
  protocol_id = Column(Integer, ForeignKey('protocol.id'))  # for SQL

  # for Python: A direct link to the client
  client = relationship("Client", backref=backref("tmodels", order_by=id))
  # for Python: A direct link to the protocol
  protocol = relationship("Protocol", backref=backref("tmodels", order_by=id))
  # for Python: A direct link to the files
  files = relationship("File", secondary=tmodel_file_association, backref=backref("tmodels", order_by=id))

  def __init__(self, mid, client_id, protocol_id):
    self.mid = mid
    self.client_id = client_id
    self.protocol_id = protocol_id

  def __repr__(self):
    return "TModel('%s', '%s')" % (self.mid, self.protocol_id)


class File(Base, bob.db.base.File):
  """Generic file container"""

  __tablename__ = 'file'

  # Key identifier for the file
  id = Column(Integer, primary_key=True)
  # Key identifier of the client associated with this file
  client_id = Column(Integer, ForeignKey('client.id'))  # for SQL
  # Unique path to this file inside the database
  path = Column(String(100), unique=True)
  # Identifier of the session
  session_id = Column(Integer)
  # Speech type
  speech_type_choices = ('p', 'l', 'r', 'f')
  speech_type = Column(Enum(*speech_type_choices))
  # Identifier of the shot
  shot_id = Column(Integer)
  # Identifier of the environment
  environment_choices = ('i', 'o')
  environment = Column(Enum(*environment_choices))
  # Identifier of the device
  device_choices = ('mobile', 'laptop')
  device = Column(Enum(*device_choices))
  # Identifier of the channel
  channel_id = Column(Integer)

  # For Python: A direct link to the client object that this file belongs to
  client = relationship("Client", backref=backref("files", order_by=id))

  def __init__(self, client_id, path, session_id, speech_type, shot_id, environment, device, channel_id):
    # call base class constructor
    bob.db.base.File.__init__(self, path=path)

    # fill the remaining bits of the file information
    self.client_id = client_id
    self.session_id = session_id
    self.speech_type = speech_type
    self.shot_id = shot_id
    self.environment = environment
    self.device = device
    self.channel_id = channel_id


class Protocol(Base):
  """MOBIO protocols"""

  __tablename__ = 'protocol'

  # Unique identifier for this protocol object
  id = Column(Integer, primary_key=True)
  # Name of the protocol associated with this object
  name = Column(String(20), unique=True)
  gender_choices = ('female', 'male')
  gender = Column(Enum(*gender_choices))

  def __init__(self, name, gender):
    self.name = name
    self.gender = gender

  def __repr__(self):
    return "Protocol('%s','%s')" % (self.name, self.gender)


class ProtocolPurpose(Base):
  """MOBIO protocol purposes"""

  __tablename__ = 'protocolPurpose'

  # Unique identifier for this protocol purpose object
  id = Column(Integer, primary_key=True)
  # Id of the protocol associated with this protocol purpose object
  protocol_id = Column(Integer, ForeignKey('protocol.id'))  # for SQL
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
