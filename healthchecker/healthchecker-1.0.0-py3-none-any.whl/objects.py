"""Helper objects definition."""

# -----------------------------------------------------------------------------
# Copyright (C) 2019 HacKan (https://hackan.net)
#
# This file is part of HealthChecker.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

import json
from hashlib import md5
from typing import Iterable, Iterator, List, Optional


class ServiceStatus(object):
    """Container for the result of a health check.

    :param url: The requested URL.
    :param alive: True for a correct response (status >= 200 but < 500), False
                  otherwise.
    :param ok: If additional checks over the response were requested, this
               value will be True if the checks passed, False otherwise.
               If no additional checks were requested, then it's True for
               successful responses (status 2xx) , False otherwise (it's always
               False if alive is False).

    """

    def __init__(self, url: Optional[str] = None,
                 alive: bool = False, ok: bool = False):
        """Container for the result of a health check.

        :param url: The requested URL.
        :param alive: True for a correct response (status >= 200 but < 500),
                      False otherwise.
        :param ok: If additional checks over the response were requested, this
                   value will be True if the checks passed, False otherwise.
                   If no additional checks were requested, then it's True for
                   successful responses (status 2xx) , False otherwise (it's always
                   False if alive is False).
        """
        self.url: str = url if url else ''
        self.alive: bool = alive
        self.ok: bool = ok

    def __bool__(self) -> bool:
        """Return the value of the ok attribute."""
        return self.ok

    def __repr__(self) -> str:
        """Return the string representation of the object."""
        return 'ServiceStatus(uid={}, url={}, alive={}, ok={})'.format(
            self.uid,
            self.url,
            self.alive,
            self.ok
        )

    def __str__(self) -> str:
        """Return a human readable representation of the object."""
        string = ''
        if self.url:
            if self.alive and self.ok:
                status = 'alive and OK'
            elif self.alive:
                status = 'alive but not OK'
            else:
                status = 'dead'
            string = '{} is {}'.format(self.url, status)
        return string

    @property
    def uid(self) -> str:
        """Return the first 8 hex digits of the md5's URL hash."""
        return md5(self.url.encode('utf-8')).hexdigest()[:8]

    def as_dict(self) -> dict:
        """Return a dict representing the object."""
        return {
            'uid': self.uid,
            'url': self.url,
            'alive': self.alive,
            'ok': self.ok,
        }

    def as_json(self, *, pretty: bool = False) -> str:
        """JSON representation of the object as a Python string.

        :param pretty: True to get a pretty-print string indented by 2 spaces.

        :return: A string with the JSON representation of the object.
        """
        indent = 2 if pretty else None
        return json.dumps(self.as_dict(), indent=indent)


class ServiceStatusList(object):
    """List of ServiceStatus objects. It is used just like any other Python list.

    :Example:

    svclist = ServiceStatusList(ServiceStatus(), ServiceStatus(), ...)
    svclist.append(ServiceStatus())
    for servicestatus in svclist: ...
    firstservicestatus = svclist[0]
    """

    def __init__(self, *args: ServiceStatus):
        """List of ServiceStatus objects."""
        self._statuses: List[ServiceStatus] = []
        self.extend(args)

    def insert(self, index: int, value: ServiceStatus) -> None:
        """Insert a ServiceStatus element in the given position."""
        self._statuses.insert(index, value)

    def append(self, value: ServiceStatus) -> None:
        """Append a ServiceStatus element at the end."""
        self._statuses.append(value)

    def pop(self) -> ServiceStatus:
        """Get the last ServiceStatus element stored, removing it."""
        return self._statuses.pop()

    def __getitem__(self, index: int) -> ServiceStatus:
        """Get the ServiceStatus element from the given position."""
        return self._statuses.__getitem__(index)

    def __iter__(self) -> Iterator:
        """Iterate over ServiceStatus elements."""
        return self._statuses.__iter__()

    def __len__(self) -> int:
        """Get the amount of ServiceStatus elements stored."""
        return len(self._statuses)

    def __delitem__(self, index: int) -> None:
        """Remove the ServiceStatus at the given position."""
        self._statuses.__delitem__(index)

    def __setitem__(self, index: int, value: ServiceStatus) -> None:
        """Set a position with a given ServiceStatus element."""
        self._statuses.__setitem__(index, value)

    def __repr__(self) -> str:
        """Return the string representation of the object."""
        return '{}([{}])'.format(self.__class__.__name__,
                                 ', '.join([repr(status) for status in self._statuses]))

    def __str__(self) -> str:
        """Return a human readable representation of the object."""
        return ', '.join([str(status) for status in self._statuses])

    def __bool__(self) -> bool:
        """Return True if every ServiceStatus element is True, else False."""
        return all(self) if len(self) else False

    def extend(self, lst: Iterable) -> None:
        """Extend the list of ServiceStatus with another ServiceStatusList."""
        self._statuses.extend(lst)

    def as_json(self, *, pretty: bool = False) -> str:
        """JSON representation of the object as a Python string.

        :param pretty: True to get a pretty-print string indented by 2 spaces.

        :return: A string with the JSON representation of the object.
        """
        indent = 2 if pretty else None
        return json.dumps([status.as_dict() for status in self._statuses],
                          indent=indent)
