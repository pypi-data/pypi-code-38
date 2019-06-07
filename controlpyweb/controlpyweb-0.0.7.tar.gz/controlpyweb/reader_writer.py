from controlpyweb.abstract_reader_writer import AbstractReaderWriter
import requests
import json
from typing import Union, Optional

from controlpyweb.errors import ControlPyWebAddressNotFoundError


class ReaderWriter(AbstractReaderWriter):

    def __init__(self, url: str, demand_address_exists: bool = True):
        """
        :param url: The address of the IO Base module from/to which IO is written
        """
        url = f'http://{url}' if 'http' not in url else url
        url = f'{url}/customState.json'
        self._url = url    # type: str
        self._io = dict()
        self._changes = dict()
        self._first_read = False
        self.demand_address_exists = demand_address_exists

    def _check_for_address(self, addr: str):
        if not self.demand_address_exists:
            return
        if not self._first_read:
            return
        if self._io is None:
            return
        if addr not in self._io:
            raise ControlPyWebAddressNotFoundError(addr)

    def _get(self):
        self._first_read = True
        r = requests.get(self._url)
        r = None if r is None else r.json()
        return r

    @staticmethod
    def _value_to_str(value):
        if isinstance(value, bool):
            value = '1' if value else '0'
        return str(value)

    @property
    def changes(self):
        """Returns a dictionary of all changes made since the last read or write"""
        return self._changes

    def dumps(self, changes_only: bool = False):
        """Returns the current IO key/values as json string"""
        if changes_only:
            return json.dumps(self._changes)
        return json.dumps(self._io)

    def flush_changes(self):
        """ Erases the collection of changes stored in memory"""
        self._changes = dict()

    def loads(self, json_str: str):
        """Replaces the current IO key/values with that from the json string"""
        self._first_read = True
        self._io = json.loads(json_str)

    def read(self, addr: str) -> Optional[Union[bool, int, float, str]]:
        """Returns the value of a single IO from the memory store"""
        if not self._first_read:
            return None
        self._check_for_address(addr)
        val = self._io.get(addr)
        return val

    def read_immediate(self, addr: str) -> object:
        """Makes a hardware call to the base module to retrieve the value of the IO. This is inneficient and should
        be used sparingly."""
        self._check_for_address(addr)
        vals = self._get()
        if vals is None:
            return None
        return vals.get(addr)

    def send_changes_to_module(self):
        """ Takes the collection of changes made using the write command and
        sends them all to the hardware collectively. """
        if self._changes is None or len(self._changes) == 0:
            return
        requests.get(self._url, params=self._changes)

    def update_from_module(self):
        """Makes a hardware call to the base module to retrieve the value of all IOs, storing their
        results in memory."""
        vals = self._get()
        if vals is not None:
            self._io = vals

    def write(self, addr: str, value: object) -> None:
        """
        Stores the write value in memory to be written as part of a group write when changes are sent to
        hardware."""
        to_str = self._value_to_str(value)
        self._io[addr] = value
        self._changes[addr] = to_str

    def write_immediate(self, addr: str, value: object):
        """
        Instead of waiting for a group write, writes the given value immediately. Note, this is not very efficient
        and should be used sparingly. """
        to_str = self._value_to_str(value)
        self._io[addr] = value
        requests.get(self._url, params={addr: to_str})

