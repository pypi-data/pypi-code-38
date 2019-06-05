# -*- coding: utf-8 -*-
# Copyright (C) 2017-2019 Team tiramisu (see AUTHORS for all contributors)
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# The original `Config` design model is unproudly borrowed from
# the rough pypy's guys: http://codespeak.net/svn/pypy/dist/pypy/config/
# the whole pypy projet is under MIT licence
# ____________________________________________________________
import re

from ..setting import undefined, Undefined, OptionBag
from ..i18n import _
from .option import Option
from .domainnameoption import DomainnameOption


class URLOption(DomainnameOption):
    __slots__ = tuple()
    proto_re = re.compile(r'(http|https)://')
    path_re = re.compile(r"^[A-Za-z0-9\-\._~:/\?#\[\]@!%\$&\'\(\)\*\+,;=]+$")
    _type = 'url'
    _display_name = _('URL')

    def _validate(self,
                  value: str,
                  option_bag: OptionBag,
                  current_opt: Option=Undefined) -> None:
        if not isinstance(value, str):
            raise ValueError(_('invalid string'))
        match = self.proto_re.search(value)
        if not match:
            raise ValueError(_('must start with http:// or '
                                'https://'))
        value = value[len(match.group(0)):]
        # get domain/files
        splitted = value.split('/', 1)
        if len(splitted) == 1:
            domain = value
            files = None
        else:
            domain, files = splitted
        # if port in domain
        splitted = domain.split(':', 1)
        if len(splitted) == 1:
            domain = splitted[0]
            port = 0
        else:
            domain, port = splitted
        if not 0 <= int(port) <= 65535:
            raise ValueError(_('port must be an between 0 and '
                                '65536'))
        # validate domainname
        super(URLOption, self)._validate(domain,
                                         option_bag,
                                         current_opt)
        super(URLOption, self)._second_level_validation(domain, False)
        # validate file
        if files is not None and files != '' and not self.path_re.search(files):
            raise ValueError(_('must ends with a valid resource name'))

    def _second_level_validation(self, value, warnings_only):
        pass
