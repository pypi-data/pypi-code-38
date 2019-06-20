#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Thu May 24 10:41:42 CEST 2012
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

"""Table models and functionality for the LFW database.
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
  """Information about the clients (identities) of the LFW database."""
  __tablename__ = 'client'

  id = Column(String(100), primary_key=True)

  def __init__(self, name):
    self.id = name

  def __lt__(self, other):
    """This function defines the order on the Client objects.
    Client objects are always ordered by their ID, in ascending order."""
    return self.id < other.id

  def __repr__(self):
    return "<Client('%s')>" % self.id


class Annotation(Base):
  __tablename__ = 'annotation'

  annotation_type_choices = ('funneled', 'idiap')

  id = Column(Integer, primary_key=True)
  file_id = Column(Integer, ForeignKey('file.id'))
  annotation_type = Column(Enum(*annotation_type_choices))
  annotations = Column(String(500))

  def __init__(self, file_id, annotation_type, annotations):
    self.file_id = file_id
    assert annotation_type in self.annotation_type_choices
    self.annotation_type = annotation_type
    self.annotations = annotations


  def _extract_funneled(self):
    """Interprets the annotation string as if it came from the funneled images."""
    splits = self.annotations.rstrip().split()
    assert len(splits) == 18
    locations = ['reyeo', 'reyei', 'leyei', 'leyeo', 'noser', 'noset', 'nosel', 'mouthr', 'mouthl']
    annotations = dict([(locations[i], (float(splits[2*i+1]), float(splits[2*i]))) for i in range(9)])
    # add eye center annotations as the center between the eye corners
    annotations['leye'] = ((annotations['leyei'][0] + annotations['leyeo'][0])/2., (annotations['leyei'][1] + annotations['leyeo'][1])/2.)
    annotations['reye'] = ((annotations['reyei'][0] + annotations['reyeo'][0])/2., (annotations['reyei'][1] + annotations['reyeo'][1])/2.)

    return annotations

  def _extract_idiap(self):
    """Interprets the annotation string as if it came from the Idiap annotations."""
    lines = self.annotations.rstrip().split('\n')
    annotations = {}
    for line in lines:
      splits = line.rstrip().split()
      if len(splits) == 2:
        # keyword annotation
        annotations[splits[0]] = splits[1]
      elif len(splits) == 3:
        # location annotation
        annotations[int(splits[0])] = (int(splits[2]), int(splits[1]))
    if 3 in annotations:
      annotations['reye'] = annotations[3]
    if 8 in annotations:
      annotations['leye'] = annotations[8]

    return annotations

  def __call__(self):
    """Interprets the annotation string and return a dictionary from location to (y,x), e.g. {'reye':(re_y, re_x), 'leye':(le_y,le_x)}"""
    if self.annotation_type == 'funneled':
      return self._extract_funneled()
    else:
      return self._extract_idiap()


def filename(client_id, shot_id):
  return client_id + "_" + "0"*(4-len(str(shot_id))) + str(shot_id)

class File(Base, bob.db.base.File):
  """Information about the files of the LFW database."""
  __tablename__ = 'file'

  # Unique key identifier for the file; here we use strings
  id = Column(Integer, primary_key=True)
  # Unique name identifier for the file
  name = Column(String(100), unique=True)
  # Identifier for the client
  client_id = Column(String(100), ForeignKey('client.id'))
  # Unique path to this file inside the database
  path = Column(String(100))
  # Identifier for the current image number of the client
  shot_id = Column(Integer)

  # a back-reference from file to client
  client = relationship("Client", backref=backref("files", order_by=id))
  # many-to-one relationship between annotations and files
  annotations = relationship("Annotation", backref=backref("file", order_by=id, uselist=False))

  def __init__(self, client_id, shot_id):
    # call base class constructor
    fn = filename(client_id, shot_id)
    bob.db.base.File.__init__(self, path = os.path.join(client_id, fn))
    self.client_id = client_id

    self.shot_id = shot_id
    self.name = fn



class People(Base):
  """Information about the people (as given in the people.txt file) of the LFW database."""
  __tablename__ = 'people'

  id = Column(Integer, primary_key=True)
  protocol = Column(Enum('train', 'test', 'fold1', 'fold2', 'fold3', 'fold4', 'fold5', 'fold6', 'fold7', 'fold8', 'fold9', 'fold10'))
  file_id = Column(String(100), ForeignKey('file.id'))

  def __init__(self, protocol, file_id):
    self.protocol = protocol
    self.file_id = file_id

  def __repr__(self):
    return "<People('%s', '%s')>" % (self.protocol, self.file_id)


class Pair(Base):
  """Information of the pairs (as given in the pairs.txt files) of the LFW database."""
  __tablename__ = 'pair'

  id = Column(Integer, primary_key=True)
  # train and test for view1, the folds for view2
  protocol = Column(Enum('train', 'test', 'fold1', 'fold2', 'fold3', 'fold4', 'fold5', 'fold6', 'fold7', 'fold8', 'fold9', 'fold10'))
  enroll_file_id = Column(String(100), ForeignKey('file.id'))
  probe_file_id = Column(String(100), ForeignKey('file.id'))
  enroll_file = relationship("File", backref=backref("enroll_files", order_by=id), primaryjoin="Pair.enroll_file_id==File.id")
  probe_file = relationship("File", backref=backref("probe_files", order_by=id), primaryjoin="Pair.probe_file_id==File.id")
  is_match = Column(Boolean)

  def __init__(self, protocol, enroll_file_id, probe_file_id, is_match):
    self.protocol = protocol
    self.enroll_file_id = enroll_file_id
    self.probe_file_id = probe_file_id
    self.is_match = is_match

  def __repr__(self):
    return "<Pair('%s', '%s', '%s', '%d')>" % (self.protocol, self.enroll_file_id, self.probe_file_id, 1 if self.is_match else 0)

