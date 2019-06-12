# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import logging
import struct

from trosnoth.utils.message import MessageBase as Message

log = logging.getLogger(__name__)


##################################
# Message-related errors
##################################

class NetworkMessageError(Exception):
    '''
    An attempt was made to process a badly formatted network message.
    '''


class MessageTypeError(NetworkMessageError):
    '''
    An attempt was made to build a NetworkMessage object from a string which
    does not represent a valid network message type.
    '''


class MessageContentsError(NetworkMessageError):
    '''
    An attempt was made to build a NetworkMessage object from a badly formatted
    message string.
    '''


##################################
# Network message metaclass
##################################

class NetworkMessageClass(type):
    '''
    Metaclass which performs declaration-time checking of attributes of
    NetworkMessage subclasses.
    '''
    def __new__(cls, name, bases, dictn):
        # Test for a single string cls.fields and make tuple.
        if isinstance(dictn.get('fields'), str):
            dictn['fields'] = (dictn['fields'],)

        # Check for use of reserved names for fields.
        for field in dictn.get('fields', ()):
            if field in ('idString', 'fields', 'packspec'):
                raise NameError('Reserved field name: %r' % (field,))

        # Do the real building.
        result = type.__new__(cls, name, bases, dictn)

        if getattr(result, 'idString'):
            # Validate the class attributes.
            if not isinstance(result.idString, bytes):
                raise TypeError('Message type idString must be byte string')
            if len(result.idString) != 4:
                raise ValueError(
                    'id string %r does not have 4 characters' % (
                        result.idString,))

            # Check for the other 2 required attributes.
            if not hasattr(result, 'packspec'):
                raise AttributeError('packspec attribute required')
            if not hasattr(result, 'fields'):
                raise AttributeError('fields attribute required')

        return result


#############################
# Network message registries
#############################

class MessageCollection(object):
    def __init__(self, *messageTypes):
        self._msgTypes = {}
        for msgType in messageTypes:
            self._registerType(msgType)

    def __iter__(self):
        return iter(self._msgTypes.values())

    def _registerType(self, msgType):
        '''
        Registers the given network message type.
        '''
        if not isinstance(msgType.idString, bytes):
            raise TypeError('Message type idString must be string')
        if len(msgType.idString) != 4:
            raise ValueError('id string %r does not have 4 characters' % (
                msgType.idString,))
        if msgType.idString in self._msgTypes:
            raise KeyError('id string %r already used for %s' % (
                msgType.idString, self._msgTypes[msgType.idString]))

        self._msgTypes[msgType.idString] = msgType

    def buildMessage(self, input):
        '''
        Builds a NetworkMessage object from the packed string.
        '''
        if not isinstance(input, bytes):
            raise TypeError('%s is not a string' % (input,))

        # Look up the id string to find the message type.
        idString = input[:4]
        try:
            msgType = self._msgTypes[idString]
        except KeyError:
            raise MessageTypeError('bad id string: %r' % (idString))

        return msgType._build(input[4:])


############################
# Network message class
############################

class NetworkMessage(Message, metaclass=NetworkMessageClass):
    '''
    Allows network messages to be defined by:
        class CustomNetMsg(NetworkMessage):
            fields = 'playerId', 'msgId', 'comment'
            packspec = 'cB*'
            idString = 'Cust'
    Parameters are as follows:
        fields - as with Message class
        packspec - a struct.pack string, except that network byte order will be
            automatically used (do not specify byte order), and the last
            character may optionally be * meaning that the rest of the message
            is considered to be a single string.
    '''
    idString = None
    trace = False       # Set to True to see where a message goes
    pumpAllEvents = False

    def __init__(self, *args, **kwargs):
        # Check that all kwargs are valid keys.
        for k in kwargs.keys():
            if k not in self.fields:
                raise TypeError('%s() got unexpected keyword argument %r' % (
                    self.__class__, k))

        # Initialise attributes based on arguments.
        Message.__init__(self, *args, **kwargs)

        # Check that packing can be performed.
        if self.idString:
            self.pack()

    def tracePoint(self, obj, method):
        if self.trace:
            log.warning('%s: %s (%s)', self, method, obj)

    def pack(self):
        '''
        Packs the field values of this message into a single string.
        '''
        # Collect the values to pack.
        values = []
        for k in self.fields:
            try:
                values.append(getattr(self, k))
            except AttributeError:
                raise ValueError('required field %s not provided' % (k,))

        # Special processing if there's a * in self.packspec.
        if self.packspec.endswith('*'):
            if not isinstance(values[-1], bytes):
                raise TypeError('%s field must be byte string' % (self.fields[-1]))
            suffix = values.pop()
            packspec = self.packspec[:-1]
        else:
            suffix = b''
            packspec = self.packspec

        # Perform the packing.
        try:
            result = struct.pack('!' + packspec, *values)
        except:
            raise Exception('%s message couldn\'t pack string %s' % (
                self.idString, str(values)))

        return self.idString + result + suffix

    @classmethod
    def _build(cls, source):
        '''
        Called by buildMessage() to build an instance of this class from a
        network message string.
        '''
        packspec = '!' + cls.packspec
        hasCoin = packspec.endswith('*')
        if hasCoin:
            packspec = packspec[:-1]
            size = struct.calcsize(packspec)
            suffix = source[size:]
            source = source[:size]
        else:
            # Verify size.
            size = struct.calcsize(packspec)
            if len(source) != size:
                raise MessageContentsError(
                    'bad message length for %s' % cls.__name__)

        # Do the actual unpacking.
        try:
            values = struct.unpack(packspec, source)
        except struct.error as E:
            raise MessageContentsError(
                'bad %s string: %s' % (cls.__name__, E.args[0]))

        # Build the message.
        if hasCoin:
            values += (suffix,)
        return cls(*values)
