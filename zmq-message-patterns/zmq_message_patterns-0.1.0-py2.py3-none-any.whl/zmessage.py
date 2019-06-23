# -*- coding: utf-8 -*-

# TODO: module description
# TODO: copyright notice

import uuid
import zlib
import base64
import logging
import collections

from six import string_types

try:
    from typing import Any, Dict, Iterable, Iterator, Tuple, TypeVar
    ZMessageType = TypeVar('ZMessageType', bound='ZMessage')
except ImportError:
    pass


class ZMessage(collections.MutableMapping):
    """
    Base class for messages received by :py:meth:`ZNode.receive()` and sent
    from :py:meth:`ZNode.send()`.

    All objects have a UUID in the :py:attr:`id` attribute and a name for the
    message type (to help the recipient decide what to do with it) in
    :py:attr:`type`.

    Payload is added and retrieved through a dictionary interface. Only strings
    are allowed as keys.

    Set :py:attr:`types` and :py:attr:`required_data` or even expand
    :py:meth:`is_valid()` to remove error checking code from
    :py:meth:`ZNode.run()`. See docstring of :py:meth:`is_valid()` for an
    example.

    To meet special marshalling requirements, customize
    :py:meth:`to_dict()` and :py:meth:`from_dict`.
    """
    types = ()  # type: Iterable[str] # list of allowed values for `type`
    required_data = ()  # type: Iterable[str]  # list of keys that must be exist in message data

    def __init__(self, mtype, **kwargs):  # type: (str, **Any) -> None
        """
        Message object.

        :param str type: message type - use this in the recipient to determine what to do with the message
        :param kwargs: payload
        """
        self.type = mtype
        self.id = str(uuid.uuid4())
        self._data = {}  # type: Dict[str, Any]
        self.update(kwargs)
        self.logger = logging.getLogger(__name__)

    def __delitem__(self, key):  # type: (str) -> Any
        if key in ('type', 'id'):
            raise KeyError('Deleting {!r} is forbidden.'.format(key))
        del self._data[key]

    def __getitem__(self, key):  # type: (str) -> Any
        if key in ('type', 'id'):
            return super(ZMessage, self).__getitem__(key)
        else:
            return self._data[key]

    def __iter__(self):  # type: () -> Iterator[str]
        return iter(self._data)

    def __len__(self):  # type: () -> int
        return len(self._data)

    def __repr__(self):  # type: () -> str
        return '{!s}(mtype={!r}, id={!r}, data={!r})'.format(self.__class__.__name__, self.type, self.id, self._data)

    def __setitem__(self, key, value):  # type: (str, Any) -> None
        if key in ('type', 'id'):
            super(ZMessage, self).__setitem__(key, value)
        else:
            if not isinstance(key, string_types):
                raise TypeError('Only strings are allowed as keys.')
            self._data[key] = value

    def __eq__(self, other):  # type: (object) -> bool
        # duck typing: allow object that is not a ZMessage (subclass) instance,
        # as long as it has attributes 'id', 'type' and a dict interface
        return all((
            self.id == getattr(other, 'id'),
            self.type == getattr(other, 'type'),
            set(self.items()) == set((key, self[key]) for key in getattr(other, '__iter__', lambda: [])())
        ))

    @staticmethod
    def decode_binary(data):  # type: (bytes) -> bytes
        """
        Helper function. Will decode data encoded with
        :py:func:`encode_binary()`.

        ::

            >>> s = b'foo'
            >>> ZMessage.decode_binary(ZMessage.encode_binary(s)) == s
            True

        :param bytes data: encoded data
        :return: decoded data
        :rtype: bytes
        """
        return zlib.decompress(base64.b64decode(data))

    @staticmethod
    def encode_binary(data):  # type: (bytes) -> bytes
        """
        Helper function. Will zlib compress `data` and base64 encode it.

        :param bytes data: data already serialized to a string representation
        :return: base64 encoded, zlib compress `data`
        :rtype: bytes
        """
        return base64.b64encode(zlib.compress(data))

    def is_valid(self):  # type: () -> Tuple[bool, str]
        """
        Check if the message object is valid. This will be run on objects
        created by :py:meth:`ZNode.receive()` and on requests before sending
        them in :py:meth:`ZNode.send()`.

        Validity checks performed here will simplify code in
        :py:meth:`ZNode.run()`.

        Set :py:attr:`types` to check if the messages value of
        :py:attr:`type` is an expected one.

        Set :py:attr:`required_data` to check if a message contains the
        expected data.

        If :py:attr:`required_data` contains an entry `foo`, and a method
        :py:meth:`is_valid_foo()` is found, then it is executed. It is expected
        to return the same as :py:meth:`is_valid()` does: a tuple(bool, str)
        with the result of the test and an optional error message.

        >>> class TestMessage(ZMessage):
        ...     types = ('test', 'shutdown')
        ...     required_data = ('foo', 'zoo')
        ...     def is_valid_foo(self):
        ...         if self['foo'].upper() != 'BAR':
        ...             return False, 'Foo must be bar.'
        ...         return True, ''
        >>> m = TestMessage('test')
        >>> m.is_valid()
        (False, "Required data 'foo' is unset in message.")
        >>> m['foo'] = 'poo'
        >>> m.is_valid()
        (False, 'Foo must be bar.')
        >>> m['foo'] = 'bar'
        >>> m.is_valid()
        (False, "Required data 'zoo' is unset in message.")
        >>> m['zoo'] = 'Python'
        >>> m.is_valid()
        (True, '')

        :return: whether the message objects attributes have the expected values and optional error message
        :rtype: tuple(bool, str)
        """
        if not isinstance(self.type, string_types):
            return False, "'type' must be a string."
        if not isinstance(self.id, string_types) or len(self.id) != 36:
            return False, "Value of 'id' must be a string containing a UUID in standard hex digits form."
        if self.types and self.type not in self.types:
            return False, "Value of 'type' must be one of {}.".format(', '.join(self.types))
        for key in self.required_data:
            if key not in self:
                return False, 'Required data {!r} is unset in message.'.format(key)
            try:
                result, reason = getattr(self, 'is_valid_{}'.format(key))()
                if not result:
                    return result, reason
            except AttributeError:
                pass
        return True, ''

    def to_dict(self):  # type: () -> dict
        """
        Marshall object to a dict for transfer over the wire.

        >>> m = ZMessage('test', foo='bar')
        >>> ZMessage.from_dict(m.to_dict()) == m
        True

        :return: marshalled object
        :rtype: dict
        """
        return {'id': self.id, 'type': self.type, 'data': self._data}

    @classmethod
    def from_dict(cls, data):  # type: (dict) -> ZMessage
        """
        Unmarshall after transfer: turn `data` into ZMessage object.

        :param dict data: arguments to create ZMessage object from, created by :py:meth:`to_dict()`
        :return: ZMessage object
        :rtype: ZMessage
        """
        assert 'id' in data
        assert 'type' in data
        assert 'data' in data

        res = cls(data['type'], **data['data'])
        res.id = data['id']
        return res


if __name__ == "__main__":
    import doctest
    doctest.testmod()
