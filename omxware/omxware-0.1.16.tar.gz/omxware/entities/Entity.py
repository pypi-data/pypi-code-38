# -*- coding: utf-8 -*-

from omxware.config import Connection


class Entity:
    """Entity Base Class"""
    _is_preview_obj = True

    _id = None
    _type = None
    _name = None
    _json = None

    _connecthdr = None
    _config = None
    _omx_token = None

    _PAGE_SIZE_DEFAULT = 25
    _PAGE_INDEX_DEFAULT = 1

    def __init__(self, connecthdr: Connection, etty_obj):
        """Constructor"""
        if etty_obj is None:
            raise Exception('Invalid Entity Object initialization. None value passed')

        elif isinstance(etty_obj, str):
            self._is_preview_obj = True
            self._id = etty_obj

        elif isinstance(etty_obj, dict):
            self._id = etty_obj['id']
            self._type = etty_obj['type']

            if self._type != 'domain':
                self._name = etty_obj['name']

            self._json = etty_obj
            self._is_preview_obj = False

        self._connecthdr = connecthdr
        self._config = self._connecthdr.config()
        self._omx_token = self._config.token()

    def connection(self):
        return self._connecthdr

    def configuration(self):
        return self._config

    def omx_token(self):
        return self._omx_token

    def id(self):
        """
        ID

        Returns:
            :return: str :   OMXWare ID
        """
        return self._id

    def type(self):
        """
        Type

        Returns:
            :return: str :   OMXWare Type
        """
        return self._type

    def name(self):
        """
        Name

        Returns:
            :return: str :   Name
        """
        return self._name

    def json(self):
        """
        As Json

        Returns:
            :return: json :   json
        """
        return self._json

    def __str__(self):
        return str(self._json)

    def is_preview_obj(self):
        return self._is_preview_obj
