#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira<tiago.pereira@idiap.ch>
# @date:   Mon Oct  19 17:41:51 CEST 2015
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

"""
Table models and functionality for the Near-Infrared and Visible-Light (NIVL) Dataset

"""

import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, or_, and_, not_
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base

import os

Base = declarative_base()

""" Defining protocols. Yes, they are static """
PROTOCOLS = ( 
              'VIS-VIS-split1', \
              'VIS-VIS-split2', \
              'VIS-VIS-split3', \
              'VIS-VIS-split4', \
              'VIS-VIS-split5', \

              'VIS-thermal-overall-split1', \
              'VIS-thermal-overall-split2', \
              'VIS-thermal-overall-split3', \
              'VIS-thermal-overall-split4', \
              'VIS-thermal-overall-split5', \

              'VIS-polarimetric-overall-split1', \
              'VIS-polarimetric-overall-split2', \
              'VIS-polarimetric-overall-split3', \
              'VIS-polarimetric-overall-split4', \
              'VIS-polarimetric-overall-split5', \

               ########## EXPRESSION

              'VIS-thermal-expression-split1', \
              'VIS-thermal-expression-split2', \
              'VIS-thermal-expression-split3', \
              'VIS-thermal-expression-split4', \
              'VIS-thermal-expression-split5', \

              'VIS-polarimetric-expression-split1', \
              'VIS-polarimetric-expression-split2', \
              'VIS-polarimetric-expression-split3', \
              'VIS-polarimetric-expression-split4', \
              'VIS-polarimetric-expression-split5', \

               ########## RANGE 1

              'VIS-thermal-R1-split1', \
              'VIS-thermal-R1-split2', \
              'VIS-thermal-R1-split3', \
              'VIS-thermal-R1-split4', \
              'VIS-thermal-R1-split5', \

              'VIS-polarimetric-R1-split1', \
              'VIS-polarimetric-R1-split2', \
              'VIS-polarimetric-R1-split3', \
              'VIS-polarimetric-R1-split4', \
              'VIS-polarimetric-R1-split5', \

               ########## RANGE 2

              'VIS-thermal-R2-split1', \
              'VIS-thermal-R2-split2', \
              'VIS-thermal-R2-split3', \
              'VIS-thermal-R2-split4', \
              'VIS-thermal-R2-split5', \

              'VIS-polarimetric-R2-split1', \
              'VIS-polarimetric-R2-split2', \
              'VIS-polarimetric-R2-split3', \
              'VIS-polarimetric-R2-split4', \
              'VIS-polarimetric-R2-split5', \

               ########## RANGE 3

              'VIS-thermal-R3-split1', \
              'VIS-thermal-R3-split2', \
              'VIS-thermal-R3-split3', \
              'VIS-thermal-R3-split4', \
              'VIS-thermal-R3-split5', \

              'VIS-polarimetric-R3-split1', \
              'VIS-polarimetric-R3-split2', \
              'VIS-polarimetric-R3-split3', \
              'VIS-polarimetric-R3-split4', \
              'VIS-polarimetric-R3-split5')


GROUPS    = ('world', 'dev')

PURPOSES   = ('train', 'enroll', 'probe')


class Client(Base):
  """
  Information about the clients (identities) of the LDHF.

  """
  __tablename__ = 'client'

  id          = Column(String(10), primary_key=True)

  def __init__(self, id):
    self.id    = id

  def __repr__(self):
    return "<Client({0})>".format(self.id)


class Annotation(Base):
  """
    - Annotation.id
    - x
    - y

  """  
  __tablename__ = 'annotation'

  file_id = Column(Integer, ForeignKey('file.id'), primary_key=True)
  le_x     = Column(Integer)
  le_y     = Column(Integer)  
  re_x     = Column(Integer)
  re_y     = Column(Integer)  


  def __init__(self, file_id, le_x, le_y, re_x, re_y):
    self.file_id = file_id
    self.le_x          = le_x
    self.le_y          = le_y
    self.re_x          = re_x
    self.re_y          = re_y


  def __repr__(self):
    return "<Annotation(file_id:{0}, le_x={1}, le_y={2}), re_x={3}, re_y={4})>".format(self.file_id, self.le_x, self.le_y, self.re_x, self.re_y)



class File(Base,  bob.db.base.File):
  """
  Information about the files of the LDHF database.

  Each file includes
  * the client id
  """
  __tablename__ = 'file'

  modality_choices = ('VIS', 'THERMAL')
  polarization_choices = ('VIS', 'S0', 'S1', 'S2', 'DP')

  id        = Column(Integer, primary_key=True)
  path      = Column(String(100), unique=True)
  client_id = Column(Integer, ForeignKey('client.id'))
  modality  = Column(Enum(*modality_choices))
  polarization  = Column(Enum(*polarization_choices))
  shot      = Column(String(3))

  # a back-reference from the client class to a list of files
  client      = relationship("Client", backref=backref("files", order_by=id))
  all_annotations = relationship("Annotation", backref=backref("file"), uselist=True)

  def __init__(self, file_id, image_name, client_id, modality, polarization, shot):
    # call base class constructor
    bob.db.base.File.__init__(self, file_id = file_id, path = image_name)    
    self.client_id     = client_id    
    self.modality      = modality
    self.polarization  = polarization
    self.shot          = shot

  
  def annotations(self, annotation_type="eyes_center"):
    assert len(self.all_annotations)==1
  
    if annotation_type=="eyes_center":
      return {'reye' : (self.all_annotations[0].re_y, self.all_annotations[0].re_x ), 'leye' : (self.all_annotations[0].le_y, self.all_annotations[0].le_x) }
    else:
      raise ValueError("Annotations type {0} invalid. Only 'eyes_center' is allowed".format(annotation_type))
      
    return data



class Protocol_File_Association(Base):
  """
  Describe the protocols
  """
  __tablename__ = 'protocol_file_association'

  protocol = Column('protocol', Enum(*PROTOCOLS), primary_key=True)
  group    = Column('group', Enum(*GROUPS), primary_key=True)
  purpose  = Column('purpose', Enum(*PURPOSES), primary_key=True)

  file_id   = Column('file_id',  Integer, ForeignKey('file.id'), primary_key=True)
  #client_id  = Column('client_id', Integer, ForeignKey('client.id'), primary_key=True)

  def __init__(self, protocol, group, purpose, file_id):
    self.protocol  = protocol
    self.group     = group
    self.purpose   = purpose
    self.file_id   = file_id
    #self.client_id = client_id    

