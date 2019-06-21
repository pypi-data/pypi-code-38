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
Table models and functionality for the Cross-Spectrum Iris/Periocular Recognition COMPETITION
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
PROTOCOLS = ('cross-eye-VIS-NIR-split1', \
             'cross-eye-VIS-NIR-split2', \
             'cross-eye-VIS-NIR-split3', \
             'cross-eye-VIS-NIR-split4', \
             'cross-eye-VIS-NIR-split5')

GROUPS = ('world', 'dev', 'eval')

PURPOSES = ('train', 'enroll', 'probe')


class Client(Base):
    """
    Information about the clients (identities) of the LDHF.

    """
    __tablename__ = 'client'

    id = Column(String(10), primary_key=True)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "<Client({0})>".format(self.id)


class File(Base, bob.db.base.File):
    """
    Information about the files of the LDHF database.

    Each file includes
    * the client id
    """
    __tablename__ = 'file'

    modality_choices = ('VIS', 'NIR')

    id = Column(Integer, primary_key=True)
    path = Column(String(100), unique=True)
    client_id = Column(Integer, ForeignKey('client.id'))
    modality = Column(Enum(*modality_choices))

    # a back-reference from the client class to a list of files
    client = relationship("Client", backref=backref("files", order_by=id))

    def __init__(self, file_id, image_name, client_id, modality):
        # call base class constructor
        bob.db.base.File.__init__(self, file_id=file_id, path=image_name)
        self.client_id = client_id
        self.modality = modality


class Protocol_File_Association(Base):
    """
    Describe the protocols
    """
    __tablename__ = 'protocol_file_association'

    protocol = Column('protocol', Enum(*PROTOCOLS), primary_key=True)
    group = Column('group', Enum(*GROUPS), primary_key=True)
    purpose = Column('purpose', Enum(*PURPOSES), primary_key=True)

    file_id = Column('file_id', Integer, ForeignKey('file.id'), primary_key=True)

    # client_id  = Column('client_id', Integer, ForeignKey('client.id'), primary_key=True)

    def __init__(self, protocol, group, purpose, file_id):
        self.protocol = protocol
        self.group = group
        self.purpose = purpose
        self.file_id = file_id
