#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Wed 19 Aug 13:43:50 2015

"""Table models and functionality for the AVSpoof DB.
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

    gender_choices = ('male', 'female')
    """Male or female speech"""

    set_choices = ('train', 'devel', 'test')
    """Possible groups to which clients may belong to"""

    id = Column(Integer, primary_key=True)
    """Key identifier for clients"""

    gender = Column(Enum(*gender_choices))
    """The gender of the subject"""

    set = Column(Enum(*set_choices))
    """Set to which this client belongs to"""

    def __init__(self, id, gender, set):
        self.id = id
        self.gender = gender
        self.set = set

    def __repr__(self):
        return "Client('%d', '%s', '%s')" % (self.id, self.gender, self.set)


class File(Base):
    """Generic file container"""

    __tablename__ = 'file'

    recording_device_choices = ('laptop', 'phone1', 'phone2')
    """List of devices used to record audio samples"""

    session_choices = ('sess1', 'sess2', 'sess3', 'sess4')
    """List of sessions during which audio samples were recorded"""

    speech_choices = ('pass', 'read', 'free')
    """Types of speech subjects were asked to say,
    pass - password, read - short text, free - 2-5 mints free speech"""

    attack_type_choices = ('undefined', 'replay', 'logical_access', 'physical_access', 'physical_access_HQ_speaker')
    """Types of attacks support"""

    attack_device_choices = ('undefined', 'laptop', 'laptop_HQ_speaker', 'phone1', 'phone2', 'voice_conversion', 'speech_synthesis')
    """Types of devices and types of access used for spoofing"""

    purpose_choices = ('real', 'attack')
    """Possible purpose of this file"""

    id = Column(Integer, primary_key=True)
    """Key identifier for files"""

    path = Column(String(200), unique=True)
    """The (unique) path to this file inside the database"""

    recording_device = Column(Enum(*recording_device_choices))
    """The device using which the data for this file was taken"""

    session = Column(Enum(*session_choices))
    """The session during which the data for this file was taken"""

    speech = Column(Enum(*speech_choices))
    """The speech type of the data for this file was taken"""

    attack_type = Column(Enum(*attack_type_choices))
    """The attack support"""

    attack_device = Column(Enum(*attack_device_choices))
    """The attack device"""

    purpose = Column(Enum(*purpose_choices))
    """Purpose of this file"""

    client_id = Column(Integer, ForeignKey('client.id'))  # for SQL
    """The client identifier to which this file is bound to"""

    # for Python
    client = relationship(Client, backref=backref('files', order_by=id))
    """A direct link to the client object that this file belongs to"""

    def __init__(self, client, path, recording_device, session, speech, attack_type, attack_device, purpose):
        self.client = client
        self.path = path
        self.recording_device = recording_device
        self.session = session
        self.speech = speech
        self.attack_type = attack_type
        self.attack_device = attack_device
        self.purpose = purpose

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
        """Returns True if this file belongs to a real access, False otherwise"""

        return self.purpose == 'real'

    def is_attack(self):
        """Returns True if this file an attack, False otherwise"""

        return self.purpose == 'attack'

    def get_attack(self):
        """Returns the full attack bame raise"""
        if not self.is_attack():
            raise RuntimeError("%s is not an attack" % self)
        if self.attack_type == 'replay':
            return self.attack_type + '_' + self.attack_device
        return self.attack_device + '_' + self.attack_type

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


class Protocol(Base):
    """AVSpoof general protocol"""

    __tablename__ = 'protocol'

    #    purpose_choices = ('antispoofing', 'verification')
    #    """What kind of protocol is it? It's true purpose"""

    id = Column(Integer, primary_key=True)
    """Unique identifier for the protocol (integer)"""

    name = Column(String(20), unique=True)
    """Protocol name"""

    #    purpose = Column(Enum(*purpose_choices))
    #    """It can one of two purposes"""


    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Protocol('%s')" % self.name


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
