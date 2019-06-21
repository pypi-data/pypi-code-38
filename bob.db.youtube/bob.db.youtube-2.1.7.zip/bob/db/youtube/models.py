#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Table models and functionality for the YouTube database.
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
  """Information about the clients (identities) of the Youtube Faces database."""
  __tablename__ = 'client'

  id = Column(Integer, primary_key=True) # The video_labels key of the meta_and_splits.mat
  name = Column(String(50))              # The name of the celebrity

  def __init__(self, id, name):
    self.id = id
    self.name = name

  def __lt__(self, other):
    """This function defines the order on the Client objects.
    Client objects are always ordered by their ID, in ascending order."""
    return self.id < other.id

  def __repr__(self):
    return "<Client('%d')>" % self.id


class Directory(Base, bob.db.base.File):
  """Information about the directories of the Youtube Faces database."""
  __tablename__ = 'directory'

  id = Column(Integer, primary_key=True)  # For the id's, we use running indices; this should correspond to the indices used in the "Splits" field

  # Identifier for the client
  client_id = Column(Integer, ForeignKey('client.id'))
  # Unique path to this file inside the database
  path = Column(String(50))
  # Identifier for the current image number of the client; this is not in consecutive order
  shot_id = Column(Integer)

  # a back-reference from file to client
  client = relationship("Client", backref=backref("directories", order_by=id))

  def __init__(self, file_id, client_id, path):
    # call base class constructor
    shot_id = int(os.path.basename(path))
    bob.db.base.File.__init__(self, file_id = file_id, path = path)
    self.client_id = client_id
    self.shot_id = shot_id


class Pair(Base):
  """Information of the pairs (as given in the pairs.txt files) of the LFW database."""
  __tablename__ = 'pair'

  id = Column(Integer, primary_key=True)
  # the folds are called 'splits' in Youtube faces, but to be consistent with LFW, we call them 'folds'
  protocol = Column(Enum('fold1', 'fold2', 'fold3', 'fold4', 'fold5', 'fold6', 'fold7', 'fold8', 'fold9', 'fold10'))

  enroll_directory_id = Column(Integer, ForeignKey('directory.id'))
  probe_directory_id = Column(Integer, ForeignKey('directory.id'))
  enroll_directory = relationship("Directory", backref=backref("enroll_directories", order_by=id), primaryjoin="Pair.enroll_directory_id==Directory.id")
  probe_directory = relationship("Directory", backref=backref("probe_directories", order_by=id), primaryjoin="Pair.probe_directory_id==Directory.id")

  enroll_client_id = Column(Integer, ForeignKey('client.id'))
  probe_client_id = Column(Integer, ForeignKey('client.id'))
  enroll_client = relationship("Client", backref=backref("enroll_clients", order_by=id), primaryjoin="Pair.enroll_client_id==Client.id")
  probe_client = relationship("Client", backref=backref("probe_clients", order_by=id), primaryjoin="Pair.probe_client_id==Client.id")

  is_match = Column(Boolean)

  def __init__(self, protocol, enroll_id, probe_id, enroll_client_id, probe_client_id, is_match):
    self.protocol = protocol
    self.enroll_directory_id = enroll_id
    self.probe_directory_id = probe_id
    self.enroll_client_id = enroll_client_id
    self.probe_client_id = probe_client_id
    self.is_match = is_match

  def __repr__(self):
    return "<Pair('%s', '%s', '%s', '%d')>" % (self.protocol, self.enroll_directory_id, self.probe_directory_id, 1 if self.is_match else 0)

