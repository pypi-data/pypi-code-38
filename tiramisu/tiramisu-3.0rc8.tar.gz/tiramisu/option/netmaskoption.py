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
from ipaddress import ip_interface, ip_network
from typing import List

from ..error import ConfigError
from ..setting import undefined, OptionBag, Undefined
from ..i18n import _
from .option import Option
from .stroption import StrOption


class NetmaskOption(StrOption):
    "represents the choice of a netmask"
    __slots__ = tuple()
    _type = 'netmask'
    _display_name = _('netmask address')

    def _validate(self,
                  value: str,
                  option_bag: OptionBag,
                  current_opt: Option=Undefined) -> None:
        if not isinstance(value, str):
            raise ValueError(_('invalid string'))
        if value.count('.') != 3:
            raise ValueError()
        for val in value.split('.'):
            if val.startswith("0") and len(val) > 1:
                raise ValueError()
        try:
            ip_network('0.0.0.0/{0}'.format(value))
        except ValueError:
            raise ValueError()

    def _cons_network_netmask(self,
                              current_opt: Option,
                              opts: List[Option],
                              vals: List[str],
                              warnings_only: bool,
                              context: 'Config'):
        if context is undefined and len(vals) != 2:
            raise ConfigError(_('network_netmask needs a network and a netmask'))
        if None in vals or len(vals) != 2:
            return
        val_netmask, val_network = vals
        opt_netmask, opt_network = opts
        try:
            ip_network('{0}/{1}'.format(val_network, val_netmask))
        except ValueError:
            if current_opt == opt_network:
                raise ValueError(_('with netmask "{0}" ("{1}")').format(val_netmask,
                                                                        opt_netmask.impl_get_display_name()))
            else:
                raise ValueError(_('with network "{0}" ("{1}")').format(val_network,
                                                                        opt_network.impl_get_display_name()))

    def _cons_ip_netmask(self,
                         current_opt: Option,
                         opts: List[Option],
                         vals: List[str],
                         warnings_only: bool,
                         context: 'config',
                         _cidr: bool=False):
        if context is undefined and len(vals) != 2:
            raise ConfigError(_('ip_netmask needs an IP and a netmask'))
        if None in vals or len(vals) != 2:
            return
        val_netmask, val_ip = vals
        opt_netmask, opt_ip = opts
        ip = ip_interface('{0}/{1}'.format(val_ip, val_netmask))
        if not _cidr and current_opt == opt_ip:
            if ip.ip == ip.network.network_address:
                raise ValueError( _('this is a network with netmask "{0}" ("{1}")'
                                    '').format(val_netmask,
                                               opt_netmask.impl_get_display_name()))
            elif ip.ip == ip.network.broadcast_address:
                raise ValueError(_('this is a broadcast with netmask "{0}" ("{1}")'
                                   '').format(val_netmask,
                                              opt_netmask.impl_get_display_name()))
        else:
            if ip.ip == ip.network.network_address:
                raise ValueError(_('IP "{0}" ("{1}") is the network'
                                   '').format(val_ip,
                                              opt_ip.impl_get_display_name()))
            elif ip.ip == ip.network.broadcast_address:
                raise ValueError(_('IP "{0}" ("{1}") is the broadcast'
                                   '').format(val_ip,
                                              opt_ip.impl_get_display_name()))
