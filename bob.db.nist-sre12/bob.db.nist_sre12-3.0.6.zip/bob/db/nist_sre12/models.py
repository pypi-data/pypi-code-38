#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
#
# Copyright (C) 2012-2014 Idiap Research Institute, Martigny, Switzerland
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

"""Table models and functionality for the NIST SRE 2012 database.
"""

import os, numpy
from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, or_, and_, not_
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import scipy.io.wavfile
import tempfile
import re
import bob.db.base

import logging                                                                                                                                               
logger = logging.getLogger("bob.db.nist_sre12")


def build_fileid (path, side):                                                                                                                               
                                                                                                                                                             
  basename = os.path.splitext(os.path.basename(path))[0]                                                                                                     
                                                                                                                                                             
  # check if basename includes sre12                                                                                                                         
  msre12 = re.match (r'.*_sre12', basename)                                                                                                                  
  bsre12 = True if msre12!= None else False                                                                                                                  
                                                                                                                                                             
  if bsre12:                                                                                                                                                 
    # basename has sre12 already                                                                                                                             
    return basename + '_' + side                                                                                                                             
  else:                                                                                                                                                      
    m = re.match (r'.*(SRE..).*',path)                                                                                                                       
    if m != None:                                                                                                                                            
      sreid = m.group(1).lower()                                                                                                                             
      return basename + '_' + sreid + '_' + side                                                                                                             
    else:                                                                                                                                                    
      return basename + '_' + side  



Base = declarative_base()

protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('file_id',  String(20), ForeignKey('file.id')))

protocolPurpose_model_association = Table('protocolPurpose_model_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('model_id',  String(20), ForeignKey('model.id')))


class ModelProbeLink(Base):
  """Model/probe associations, i.e. trial target speaker / test segment"""

  __tablename__ = 'model_probe_link'

  model_id = Column(String(20), ForeignKey('model.id'), primary_key=True)
  file_id = Column(String(20), ForeignKey('file.id'), primary_key=True)
  protocol_id = Column(String(20), ForeignKey('protocol.id'), primary_key=True)

  def __init__(self, model_id, file_id, protocol_id):
    self.model_id = model_id
    self.file_id = file_id
    self.protocol_id = protocol_id

  def __repr__(self):
    return "ModelProbe(%s, %s)" % (self.model_id, self.file_id)

class ModelEnrollLink(Base):
  """Model/enroll associations, i.e. files used for enrolling this model"""

  __tablename__ = 'model_enroll_link'

  model_id = Column(String(20), ForeignKey('model.id'), primary_key=True)
  file_id = Column(String(20), ForeignKey('file.id'), primary_key=True)
  protocol_id = Column(String(20), ForeignKey('protocol.id'), primary_key=True)

  def __init__(self, model_id, file_id, protocol_id):
    self.model_id = model_id
    self.file_id = file_id
    self.protocol_id = protocol_id

  def __repr__(self):
    return "ModelEnroll(%s, %s)" % (self.model_id, self.file_id)


class Model(Base):
  """Database models, marked by an integer identifier and the group they belong to"""

  __tablename__ = 'model'

  # Key identifier for the model
  id = Column(String(20), primary_key=True)
  gender_choices = ('male', 'female')
  gender = Column(Enum(*gender_choices))
  client_id = Column(String(20))

  def __init__(self, id, client_id, gender):
    self.id = id
    self.client_id = client_id
    self.gender = gender

  def __repr__(self):
    return "Model(%s, %s, %s)" % (self.id, self.gender, self.client_id)


class File(Base, bob.db.base.File):
  """Generic file container"""

  __tablename__ = 'file'

  # Key identifier for the file
  id = Column(String(20), primary_key=True)
  # Unique path to this file inside the database
  path = Column(String(150))
  side_choices = ('a','b')
  side = Column(Enum(*side_choices))
  client_id = Column(String(20))


  def __init__(self, client_id, path, side):
    # call base class constructor
    self.id = build_fileid (path, side)
    self.path = path
    self.client_id = client_id
    self.side = side

  def __repr__(self):
    """This function describes how to convert a File object into a string."""
    return "<File('%s': '%s', '%s', '%s')>" % (str(self.id), str(self.path), str(self.side), str(self.client_id))

  def make_path(self, directory=None, extension='.sph', add_side=True):
    """Wraps the current path so that a complete path is formed

    Keyword Parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.jpg`` or
      ``.hdf5``.

    Returns a string containing the newly generated file path.
    """
    # assure that directory and extension are actually strings
    # create the path
    if add_side:
      return str(os.path.join((directory or ''),self.path + '-' + self.side + (extension or '')) )
    else:
      return str(os.path.join((directory or ''),self.path + (extension or ''))  )

  def load(self, directory=None, extension='.sph'):
    """Loads the data at the specified location and using the given extension.
    Override it if you need to load differently.

    Keyword Parameters:

    data
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory
      [optional] If not empty or None, this directory is prefixed to the final
      file destination

    extension
      [optional] The extension of the filename - this will control the type of
      output and the codec for saving the input blob.

    """
    # get the path
    abspath = self.make_path(directory or '', extension or '', add_side=False)
#    logger.warn('abspath=' + abspath + '\n')
    with tempfile.NamedTemporaryFile(suffix='.wav') as ftmp:
      cmd = ['sph2pipe']
      if self.side == 'a':
        cmd += [
          '-c 1',
          '-p',
          '-f rif',
          abspath,
          ftmp.name]
      else:
        cmd += [
          '-c 2',
          '-p',
          '-f rif',
          abspath,
          ftmp.name]
#      logger.warn('/bin/bash -c \"' + ' '.join(cmd) + '\"')
#      os.system ('/bin/bash -c \"' + ' '.join(cmd) + '\"')
      os.system (' '.join(cmd))
#      logger.warn('after cmd' + '\n')

#      if os.path.isfile(ftmp.name):
#        logger.warn('exists')

      # read mono wav file
      rate, audio = scipy.io.wavfile.read(ftmp.name)
      data = numpy.cast['float'](audio)
      return rate, data
    
class Protocol(Base):
  """NIST SRE 2012 protocols"""

  __tablename__ = 'protocol'

  # Unique identifier for this protocol object
  id = Column(Integer, primary_key=True)
  # Name of the protocol associated with this object
  name = Column(String(20), unique=True)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Protocol('%s')" % (self.name)

class ProtocolPurpose(Base):
  """NIST SRE 2012 purposes"""

  __tablename__ = 'protocolPurpose'

  # Unique identifier for this protocol purpose object
  id = Column(Integer, primary_key=True)
  # Id of the protocol associated with this protocol purpose object
  protocol_id = Column(Integer, ForeignKey('protocol.id')) # for SQL
  # Group associated with this protocol purpose object
  group_choices = ('eval',)
  sgroup = Column(Enum(*group_choices))
  # Purpose associated with this protocol purpose object
  purpose_choices = ('enroll', 'probe')
  purpose = Column(Enum(*purpose_choices))

  # For Python: A direct link to the Protocol object that this ProtocolPurpose belongs to
  protocol = relationship("Protocol", backref=backref("purposes", order_by=id))
  # For Python: A direct link to the File objects associated with this ProtcolPurpose
  files = relationship("File", secondary=protocolPurpose_file_association, backref=backref("protocolPurposes", order_by=id))
  # For Python: A direct link to the model objects associated with this ProtcolPurpose
  models = relationship("Model", secondary=protocolPurpose_model_association, backref=backref("protocolPurposes", order_by=id))

  def __init__(self, protocol_id, sgroup, purpose):
    self.protocol_id = protocol_id
    self.sgroup = sgroup
    self.purpose = purpose

  def __repr__(self):
    return "ProtocolPurpose('%s', '%s', '%s')" % (self.protocol.name, self.sgroup, self.purpose)

