#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Fri May 11 17:20:46 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Table models and functionality for the GBU database.
"""

import os
from sqlalchemy import Table, Column, Integer, String, ForeignKey, or_, and_
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base

Base = declarative_base()

def client_id_from_signature(signature):
  return int(signature[4:])


class Client(Base):
  """The client of the GBU database consists of an integral ID
  as well as the 'signature' as read from the file lists."""
  __tablename__ = 'client'

  id = Column(Integer, primary_key=True)

  def __init__(self, signature):
    self.id = client_id_from_signature(signature)

  def __repr__(self):
    return "<Client(%d)>" % (self.id)


class Annotation(Base):
  """Annotations of the GBU database consists only of the left and right eye positions.
  There is exactly one annotation for each file."""
  __tablename__ = 'annotation'

  id = Column(Integer, primary_key=True)
  file_id = Column(Integer, ForeignKey('file.id'))

  le_x = Column(Integer) # left eye
  le_y = Column(Integer)
  re_x = Column(Integer) # right eye
  re_y = Column(Integer)

  def __init__(self, file_id, eyes):
    self.file_id = file_id

    assert len(eyes) == 4
    self.re_x = int(eyes[0])
    self.re_y = int(eyes[1])
    self.le_x = int(eyes[2])
    self.le_y = int(eyes[3])

  def __call__(self):
    """Returns the annotations of this database in a dictionary: {'reye' : (re_y, re_x), 'leye' : (le_y, le_x)}."""
    return {'reye' : (self.re_y, self.re_x), 'leye' : (self.le_y, self.le_x) }

  def __repr__(self):
    return "<Annotation('%s': 'reye'=%dx%d, 'leye'=%dx%d)>" % (self.file_id, self.re_y, self.re_x, self.le_y, self.le_x)


class File(Base, bob.db.base.File):
  """The file of the GBU database consists of an integral id
  as well as the 'presentation' as read from the file lists.
  Each file has one annotation and one associated client."""
  __tablename__ = 'file'

  id = Column(Integer, primary_key=True)
  client_id = Column(Integer, ForeignKey('client.id')) # The client id; should start with nd1
  path = Column(String(100), unique=True) # The relative path where to find the file

  client = relationship("Client", backref=backref("files", order_by=id))
  # one-to-one relationship between annotations and files
  annotation = relationship("Annotation", backref=backref("file", order_by=id, uselist=False), uselist=False)

  def __init__(self, presentation, signature, path):
    # call base class function
    bob.db.base.File.__init__(self, path = path)
    self.client_id = client_id_from_signature(signature)
    # signature and presentation are not stored, but needed for creation
    self.signature = signature
    self.presentation = presentation


# The subworld file association table is used as a many-to-many relationship between files and sub-worlds.
subworld_file_association = Table('subworld_file_association', Base.metadata,
  Column('subworld_id', Integer, ForeignKey('subworld.id')),
  Column('file_id',  Integer, ForeignKey('file.id')))

class Subworld(Base):
  """The subworld class defines different training set sizes.
  It is created from the 'x1', 'x2', 'x4' and 'x8' training lists from the GBU database."""
  __tablename__ = 'subworld'

  subworld_choices = ('x1', 'x2', 'x4', 'x8')

  id = Column(Integer, primary_key=True)
  name = Column(Enum(*subworld_choices))

  # back-reference from the file to the subworlds
  files = relationship("File", secondary=subworld_file_association, backref=backref("subworlds", order_by=id))

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "<Subworld('%s')>" % (self.name)


# The protocol file association table is used as a many-to-many relationship between files and protocols.
# Though I am not sure if files are actually shared between protocols...
protocol_file_association = Table('protocol_file_association', Base.metadata,
  Column('protocol_id', Integer, ForeignKey('protocol.id')),
  Column('file_id',  Integer, ForeignKey('file.id')))

class Protocol(Base):
  """The protocol class stores both the protocol name,
  as well as the purpose."""
  __tablename__ = 'protocol'

  protocol_choices = ('Good', 'Bad', 'Ugly')
  purpose_choices = ('enroll', 'probe')

  id = Column(Integer, primary_key=True)
  name = Column(Enum(*protocol_choices)) # one of the protocol names
  purpose = Column(Enum(*purpose_choices)) # one o the choices, enroll or probe

  # A direct link to the File objects associated with this Protocol
  files = relationship("File", secondary=protocol_file_association, backref=backref("protocols", order_by=id))

  def __init__(self, name, purpose):
    self.name = name
    self.purpose = purpose

  def __repr__(self):
    return "<Protocol('%s', '%s')>" % (self.name, self.purpose)
