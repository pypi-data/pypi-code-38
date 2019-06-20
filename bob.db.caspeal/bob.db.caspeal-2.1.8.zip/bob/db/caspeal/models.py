#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Mon Dec 10 14:29:51 CET 2012
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

"""Table models and functionality for the CAS-PEAL database.
"""

import sqlalchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, or_, and_, not_
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
import os

import bob.db.base

Base = declarative_base()

class Client(Base):
  """Information about the clients (identities) of the CAS-PEAL database"""
  __tablename__ = 'client'

  # We define the possible values for the member variables as STATIC class variables
  gender_choices = ('F', 'M')
  age_choices = ('Y', 'M', 'O')

  id = Column(Integer, primary_key=True)
  gender = Column(Enum(*gender_choices))
  age = Column(Enum(*age_choices))

  def __init__(self, client_type, client_id):
    """Creates a client name by parsing the given first two part of the filename"""
    assert client_type[0] in 'FM'
    assert client_type[1] in 'YMO'
    self.id = int(client_id)
    self.gender = client_type[0]
    self.age = client_type[1]

  def __repr__(self):
    return "<Client('%s%s_%06d')>" % (self.gender, self.age, self.id)


class Annotation(Base):
  """Annotations of the CAS-PEAL database consists only of the left and right eye positions.
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
    return {'reye' : (self.re_y, self.re_x), 'leye' : (self.le_y, self.le_x)}

  def __repr__(self):
    return "<Annotation('%s': 'reye'=%dx%d, 'leye'=%dx%d)>" % (self.file_id, self.re_y, self.re_x, self.le_y, self.le_x)


class File(Base, bob.db.base.File):
  """Information about the files of the CAS-PEAL face database. Each file includes

  * the session
  * the expression
  * the pose
  * the lighting
  * the camera distance
  * the accessory
  * the background
  * a privacy field describing whether the image file might be published in papers
  * the client id
  * the path
  """
  import itertools

  __tablename__ = 'file'

  # We define the possible values for the member variables as STATIC class variables
  purpose_choices = ('world', 'enroll', 'probe')
  lighting_type_choices = ('E', 'F', 'L') # ('ambient', 'fluorescent', 'incandescent')
  elevation_choices = ('U', 'M', 'D') # for both pose and lighting
  lighting_azimuth_choices = ('-90', '-45', '+00', '+45', '+90')  # for both pose and lighting
  pose_azimuth_choices = ('-90', '-67', '-45', '-30', '-22', '-15', '+00', '+15', '+22', '+30', '+45', '+67', '+90')  # for both pose and lighting
  expression_choices = ('N', 'L', 'F', 'S', 'C', 'O') # ('neutral', 'laughing', 'frowning', 'surprising', 'eyes_closed', 'mouth_open')
  distance_choices = list(range(3))
  accessory_choices = list(range(7)) # ('none', 'hat_1', 'hat_2', 'hat_3', 'glasses_1', 'glasses_2', 'glasses_3')
  session_choices = list(range(3)) # ('first', 'second', 'third')
  background_choices = ('B', 'R', 'D', 'Y', 'W') #('blue', 'red', 'dark', 'yellow', 'white')

  lighting_choices = ["%s%s%s"%(t,e,a) for (t,e,a) in itertools.product(lighting_type_choices, elevation_choices, lighting_azimuth_choices)] # not all these illuminations really exist
  pose_choices = ["%s%s"%(e,a) for (e,a) in itertools.product(elevation_choices, pose_azimuth_choices)] # maybe, not all of these poses exists

  id = Column(Integer, primary_key=True)
  path = Column(String(100), unique=False) # << NOTE: some files's are used in several lists (training  and  enroll or probe). Hence, unfortunately, the paths are NOT UNIQUE
  client_id = Column(Integer, ForeignKey('client.id'))
  protocol_id = Column(Integer, ForeignKey('protocol.id'))

  purpose = Column(Enum(*purpose_choices))

  lighting = Column(Enum(*lighting_choices))
  pose = Column(Enum(*pose_choices))
  expression = Column(Enum(*expression_choices))
  distance = Column(Integer)
  accessory = Column(Integer)
  session = Column(Integer)
  background = Column(Integer)
  privacy = Column(Boolean)

  # one-to-one relationship between annotations and files
  annotation = relationship("Annotation", backref=backref("file", order_by=id, uselist=False), uselist=False)
  # a back-reference from the client class to a list of files
  client = relationship("Client", backref=backref("files", order_by=id))
  protocol = relationship("Protocol", backref=backref("files", order_by=id))

  def __init__(self, image_path, protocol):

    # set protocol id
    self.protocol_id = protocol.id
    # set purpose
    self.purpose = 'world' if protocol.name == 'training' else 'enroll' if protocol.name == 'gallery' else 'probe'

    # replace the "\" with "/" to obtain the path
    path = os.path.join(*image_path.split("\\"))

    # split the image name from the path
    image_name = os.path.basename(path)
    # obtain information about the image
    splits = image_name.split('_')
    assert len(splits) == 12

    # client id
    client_id = int(splits[1])
    # call base class constructor
    bob.db.base.File.__init__(self, path = path)
    self.client_id = client_id

    # lighting
    assert splits[2][0] == 'I'
    self.lighting = splits[2][1:]
    # pose
    assert splits[3][0] == 'P'
    self.pose = splits[3][1:5]
    # expression
    assert splits[4][0] == 'E'
    self.expression = splits[4][1]
    # accessory
    assert splits[5][0] == 'A'
    self.accessory = int(splits[5][1:])
    # distance
    assert splits[6][0] == 'D'
    self.distance = int(splits[6][1:])
    # session
    assert splits[7][0] == 'T'
    self.session = int(splits[7][1:])
    # background
    assert splits[8][0] == 'B'
    self.background = splits[8][1]
    # field 9 is left out
    # privacy
#    assert splits[10][0] == 'R' << this check doesn't work, there is at least one file containing a "D" at this position...
    self.privacy = splits[10][1] == '1' and self.client_id < 100 # (see license agreement)

  def lighting_type(self):
    return {'E':'ambient','F':'fluorescent','L':'incandescent'}[self.lighting[0]]

  def lighting_elevation(self):
    return {'U':'+45','M':'+00','D':'-45'}[self.lighting[1]]

  def lighting_azimuth(self):
    return self.lighting[2:5]

  def pose_elevation(self):
    return {'U':'Up','M':'Into','D':'Down'}[self.lighting[0]]

  def pose_azimuth(self):
    return self.pose[1:4]

  def expression_type(self):
    return {'N':'neutral','L':'laughing','F':'frowning','S':'surprising','C':'eyes_closed','O':'mouth_open'}[self.expression[0]]

  def accessory_type(self):
    return ('none','hat_1','hat_2','hat_3','glasses_1','glasses_2','glasses_3')[self.accessory]

  def background_type(self):
    return {'B':'blue','R':'red','D':'dark','Y':'yellow','W':'white'}[self.background]



class Protocol(Base):
  """The probe protocols of the CAS-PEAL database. Training and enrollment is identical for all protocols of CAS-PEAL."""
  __tablename__ = 'protocol'

  # query protocols start from index 2
  protocol_choices = ('training', 'gallery', 'accessory', 'aging', 'background', 'distance', 'expression', 'lighting', 'pose')

  id = Column(Integer, primary_key=True)
  name = Column(Enum(*protocol_choices))

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "<Protocol('%d', '%s')>" % (self.id, self.name)

