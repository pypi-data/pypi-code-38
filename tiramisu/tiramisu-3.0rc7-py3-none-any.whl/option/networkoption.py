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
from ipaddress import ip_address, ip_network

from ..setting import undefined
from ..i18n import _
from .option import Option


class NetworkOption(Option):
    "represents the choice of a network"
    __slots__ = tuple()
    _type = 'network'
    _display_name = _('network address')

    def __init__(self,
                 name,
                 doc,
                 default=None,
                 default_multi=None,
                 requires=None,
                 multi=False,
                 callback=None,
                 callback_params=None,
                 validator=None,
                 validator_params=None,
                 properties=None,
                 warnings_only=False,
                 cidr=False):
        extra = {'_cidr': cidr}
        super().__init__(name,
                         doc,
                         default=default,
                         default_multi=default_multi,
                         callback=callback,
                         callback_params=callback_params,
                         requires=requires,
                         multi=multi,
                         validator=validator,
                         validator_params=validator_params,
                         properties=properties,
                         warnings_only=warnings_only,
                         extra=extra)

    def _validate(self,
                  value,
                  *args,
                  **kwargs):
        if not isinstance(value, str):
            raise ValueError(_('invalid string'))
        if value.count('.') != 3:
            raise ValueError()
        cidr = self.impl_get_extra('_cidr')
        if cidr:
            if '/' not in value:
                raise ValueError(_('must use CIDR notation'))
            value_ = value.split('/')[0]
        else:
            value_ = value
        for val in value_.split('.'):
            if val.startswith("0") and len(val) > 1:
                raise ValueError()
        try:
            ip_network(value)
        except ValueError:
            raise ValueError()

    def _second_level_validation(self,
                                 value,
                                 warnings_only):
        if ip_network(value).network_address.is_reserved:
            if warnings_only:
                msg = _("shouldn't be reserved network")
            else:
                msg = _("mustn't be reserved network")
            raise ValueError(msg)
