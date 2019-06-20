#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Wed Jul  4 14:12:51 CEST 2012
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
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

"""Table models and functionality for the AR face database.
"""

import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, or_, and_, not_
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base

import os

Base = declarative_base()


class Client(Base):
  """Information about the clients (identities) of the AR face database"""
  __tablename__ = 'client'

  # We define the possible values for the member variables as STATIC class
  # variables
  gender_choices = ('m', 'w')
  group_choices = ('world', 'dev', 'eval')

  id = Column(String(100), primary_key=True)
  gender = Column(Enum(*gender_choices))
  sgroup = Column(Enum(*group_choices))

  def __init__(self, id, group):
    self.id = id
    self.gender = id[0:1]
    self.sgroup = group

  def __repr__(self):
    return "<Client('%s')>" % self.id


class File(Base, bob.db.base.File):
  """Information about the files of the AR face database. Each file includes

  * the session (first, second)
  * the expression (neutral, smile, anger, scream)
  * the illumination (front, left, right, all)
  * the occlusion (none, sunglasses, scarf)
  * the client id
  """
  __tablename__ = 'file'

  # We define the possible values for the member variables as STATIC class
  # variables
  session_choices = ('first', 'second')
  purpose_choices = ('enroll', 'probe')
  expression_choices = ('neutral', 'smile', 'anger', 'scream')
  illumination_choices = ('front', 'left', 'right', 'all')
  occlusion_choices = ('none', 'sunglasses', 'scarf')

  id = Column(String(100), primary_key=True)
  path = Column(String(100), unique=True)
  client_id = Column(String(100), ForeignKey('client.id'))
  session = Column(Enum(*session_choices))
  purpose = Column(Enum(*purpose_choices))
  expression = Column(Enum(*expression_choices))
  illumination = Column(Enum(*illumination_choices))
  occlusion = Column(Enum(*occlusion_choices))

  # a back-reference from the client class to a list of files
  client = relationship("Client", backref=backref("files", order_by=id))
  annotation = relationship(
      "Annotation", backref=backref("file"), uselist=False)

  def __init__(self, image_name):
    # call base class constructor
    bob.db.base.File.__init__(self, path=image_name, file_id=image_name)
    self.client_id = image_name[:5]

    # get shot id
    shot_id = int(os.path.splitext(image_name)[0][6:])
    # automatically fill member variables according to shot id
    self.session = self.session_choices[int((shot_id - 1) / 13)]
    shot_id = (shot_id - 1) % 13 + 1

    self.purpose = self.purpose_choices[0 if shot_id == 1 else 1]

    self.expression = self.expression_choices[
        shot_id - 1] if shot_id in (2, 3, 4) else self.expression_choices[0]

    self.illumination = self.illumination_choices[shot_id - 4]  if shot_id in (5, 6, 7) else \
        self.illumination_choices[shot_id - 8]  if shot_id in (9, 10) else \
        self.illumination_choices[shot_id - 11] if shot_id in (12, 13) else \
        self.illumination_choices[0]

    self.occlusion = self.occlusion_choices[1] if shot_id in (8, 9, 10) else \
        self.occlusion_choices[2] if shot_id in (11, 12, 13) else \
        self.occlusion_choices[0]


class Annotation(Base):
  """Annotations of the AR face database consists only of the left and right eye positions.
  There is exactly one annotation for each file."""
  __tablename__ = 'annotation'

  id = Column(Integer, primary_key=True)
  file_id = Column(Integer, ForeignKey('file.id'))

  le_x = Column(Integer)  # left eye
  le_y = Column(Integer)
  re_x = Column(Integer)  # right eye
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
    return {'reye': (self.re_y, self.re_x), 'leye': (self.le_y, self.le_x)}

  def __repr__(self):
    return "<Annotation('%s': 'reye'=%dx%d, 'leye'=%dx%d)>" % (self.file_id, self.re_y, self.re_x, self.le_y, self.le_x)


class Protocol(Base):
  """The protocols of the AR face database."""
  __tablename__ = 'protocol'

  protocol_choices = ('all', 'expression', 'illumination',
                      'occlusion', 'occlusion_and_illumination')

  id = Column(Integer, primary_key=True)
  name = Column(Enum(*protocol_choices))
  session = Column(Enum(*File.session_choices), ForeignKey('file.session'))
  expression = Column(Enum(*File.expression_choices),
                      ForeignKey('file.expression'))
  illumination = Column(Enum(*File.illumination_choices),
                        ForeignKey('file.illumination'))
  occlusion = Column(Enum(*File.occlusion_choices),
                     ForeignKey('file.occlusion'))

  def __init__(self, protocol, session, expression='neutral', illumination='front', occlusion='none'):
    self.name = protocol
    self.session = session
    self.expression = expression
    self.illumination = illumination
    self.occlusion = occlusion

  def __repr__(self):
    return "<Protocol('%s', '%s', '%s', '%s', '%s')>" % (self.name, self.session, self.expression, self.illumination, self.occlusion)
