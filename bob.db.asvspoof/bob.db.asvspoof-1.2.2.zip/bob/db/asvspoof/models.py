#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Wed 19 Aug 13:43:50 2015

"""Table models and functionality for the ASVspoof DB.
"""

import os
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
import bob

Base = declarative_base()


class Client(Base):
    """Database clients, marked by an integer identifier and the set they belong
    to"""

    __tablename__ = 'client'

    gender_choices = ('male', 'female', 'undefined')
    """Male or female speech"""

    group_choices = ('train', 'dev', 'eval')
    """Possible groups to which clients may belong to"""

    id = Column(String, primary_key=True)
    """Key identifier for clients"""

    gender = Column(Enum(*gender_choices))
    """The gender of the subject"""

    group = Column(Enum(*group_choices))
    """Group to which this client belongs to"""

    def __init__(self, id, gender, group):
        self.id = id
        self.gender = gender
        self.group = group

    def __repr__(self):
        return "Client('%s', '%s', '%s')" % (self.id, self.gender, self.group)


class Protocol(Base):
    """Database clients, marked by an integer identifier and the set they belong
    to"""

    __tablename__ = 'protocol'

    id = Column(Integer, primary_key=True)
    """Key identifier for Protocols"""

    name = Column(String(20))
    """Protocol name"""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Protocol('%s')" % (self.name)

class File(Base):
    """Generic file container"""

    __tablename__ = 'file'

    group_choices = ('train', 'dev', 'eval')
    """Possible groups of this file"""

    attacktype_choices = ('undefined', 'unknown', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10')
    """Possible attacks this file is meant for"""

    purpose_choices = ('real', 'attack', 'impostor', 'enroll')
    """Possible purpose of this file"""

    id = Column(Integer, primary_key=True)
    """Key identifier for files"""

    group = Column(Enum(*group_choices))
    """Group of this file"""

    attacktype = Column(Enum(*attacktype_choices))
    """Type of attack this file is meant for"""

    purpose = Column(Enum(*purpose_choices))
    """Purpose of this file"""

    path = Column(String(200), unique=True)
    """The (unique) path to this file inside the database"""

    client_id = Column(String, ForeignKey('client.id'))  # for SQL
    """The client identifier to which this file is bound to"""

    # for Python
    client = relationship(Client, backref=backref('files', order_by=id))
    """A direct link to the client object that this file belongs to"""

    def __init__(self, client, purpose, attack_type, path, group):
        self.client = client
        self.purpose = purpose
        self.attacktype = attack_type
        self.path = path
        self.group = group

    def __repr__(self):
        return "File('%s')" % self.path

    def make_path(self, directory=None, extension=None):
        """Wraps the current path so that a complete path is formed

        Keyword parameters:

        directory
            An optional directory name that will be prefixed to the returned result.

        extension
            An optional extension that will be suffixed to the returned filename. The
            extension normally includes the leading ``.`` character as in ``.wav`` or
            ``.hdf5``.

        Returns a string containing the newly generated file path.
        """

        if not directory: directory = ''
        if not extension: extension = ''

        return str(os.path.join(directory, self.path + extension))

    def audiofile(self, directory=None):
        """Returns the path to the database audio file for this object

        Keyword parameters:

        directory
            An optional directory name that will be prefixed to the returned result.

        Returns a string containing the video file path.
        """

        return self.make_path(directory, '.wav')

    def is_real(self):
        """Returns True if this file is real data, False otherwise"""

        return self.purpose == 'real'

    def is_attack(self):
        """Returns True if this file an attack, False otherwise"""

        return self.purpose == 'attack'

    def is_impostor(self):
        """Returns True if this file an attack, False otherwise"""

        return self.purpose == 'impostor'

    def is_enroll(self):
        """Returns True if this file in enrollment set, False otherwise"""

        return self.purpose == 'enroll'

    def load(self, directory=None, extension='.hdf5'):
        """Loads the data at the specified location and using the given extension.

        Keyword parameters:

        data
            The data blob to be saved (normally a :py:class:`numpy.ndarray`).

        directory
            [optional] If not empty or None, this directory is prefixed to the final
            file destination

        extension
            [optional] The extension of the filename - this will control the type of
            output and the codec for saving the input blob.
        """
        return bob.io.base.load(self.make_path(directory, extension))

    def save(self, data, directory=None, extension='.hdf5'):
        """Saves the input data at the specified location and using the given
        extension.

        Keyword parameters:

        data
            The data blob to be saved (normally a :py:class:`numpy.ndarray`).

        directory
            [optional] If not empty or None, this directory is prefixed to the final
            file destination

        extension
            [optional] The extension of the filename - this will control the type of
            output and the codec for saving the input blob.
        """

        path = self.make_path(directory, extension)
        bob.io.base.create_directories_safe(os.path.dirname(path))
        bob.io.base.save(data, path)

class ProtocolFiles(Base):
    """Database clients, marked by an integer identifier and the set they belong
    to"""

    __tablename__ = 'protocolfiles'

    id = Column(Integer, primary_key=True)
    """Key identifier for Protocols"""

    protocol_id = Column(String, ForeignKey('protocol.id'))  # for SQL
    """The protocol identifier that the file is linked to"""

    # for Python
    protocol = relationship(Protocol, backref=backref('protocolfiles', order_by=id))
    """A direct link to the protocol object that refers to the given file"""

    file_id = Column(String, ForeignKey('file.id'))  # for SQL
    """The file id that the protocol references"""

    # for Python
    file = relationship(File, backref=backref('protocolfiles', order_by=id))
    """A direct link to the file object that the protocol references"""


    def __init__(self, protocol, file):
        self.protocol = protocol
        self.file = file

    def __repr__(self):
        return "ProtocolFiles('%s, %s')" % (self.protocol_id, self.file_id)

