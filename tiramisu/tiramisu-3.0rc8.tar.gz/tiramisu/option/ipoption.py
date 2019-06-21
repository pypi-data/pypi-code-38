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
from ipaddress import ip_address, ip_interface, ip_network

from ..error import ConfigError
from ..setting import undefined, Undefined, OptionBag
from ..i18n import _
from .option import Option
from .stroption import StrOption
from .netmaskoption import NetmaskOption
from .networkoption import NetworkOption


class IPOption(StrOption):
    "represents the choice of an ip"
    __slots__ = tuple()
    _type = 'ip'
    _display_name = _('IP')

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
                 private_only=False,
                 allow_reserved=False,
                 warnings_only=False,
                 cidr=False,
                 _extra=None):
        if _extra is None:
            extra = {}
        else:
            extra = _extra
        extra['_private_only'] = private_only
        extra['_allow_reserved'] = allow_reserved
        extra['_cidr'] = cidr
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
                  value: str,
                  option_bag: OptionBag,
                  current_opt: Option=Undefined) -> None:
        # sometimes an ip term starts with a zero
        # but this does not fit in some case, for example bind does not like it
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
        # 'standard' validation
        try:
            if not cidr:
                ip_address(value)
            else:
                ip_interface(value)
        except ValueError:
            raise ValueError()

    def _second_level_validation(self,
                                 value,
                                 warnings_only):
        ip = ip_interface(value)
        if not self.impl_get_extra('_allow_reserved') and ip.is_reserved:
            if warnings_only:
                msg = _("shouldn't be reserved IP")
            else:
                msg = _("mustn't be reserved IP")
            raise ValueError(msg)
        if self.impl_get_extra('_private_only') and not ip.is_private:
            if warnings_only:
                msg = _("should be private IP")
            else:
                msg = _("must be private IP")
            raise ValueError(msg)
        if '/' in value:
            net = NetmaskOption(self.impl_getname(),
                                self.impl_get_display_name(),
                                str(ip.netmask))
            net._cons_ip_netmask(self,
                                 (net, self),
                                 (str(ip.netmask), str(ip.ip)),
                                 warnings_only,
                                 None,
                                 True)

    def _cons_in_network(self,
                         current_opt,
                         opts,
                         vals,
                         warnings_only,
                         context):
        if len(opts) == 2 and isinstance(opts[0], IPOption) and \
                opts[0].impl_get_extra('_cidr') == False and \
                isinstance(opts[1], NetworkOption) and \
                opts[1].impl_get_extra('_cidr') == True:
            if None in vals:
                return
            ip, network = vals
            network_obj = ip_network(network)
            if ip_interface(ip) not in network_obj:
                msg = _('"{0}" is not in network "{1}" ("{2}")')
                raise ValueError(msg.format(ip,
                                            network,
                                            opts[1].impl_get_display_name()))
            # test if ip is not network/broadcast IP
            netmask = NetmaskOption(self.impl_getname(),
                                    self.impl_get_display_name(),
                                    str(network_obj.netmask))
            netmask._cons_ip_netmask(self,
                                     (netmask, self),
                                     (str(network_obj.netmask), str(ip)),
                                     warnings_only,
                                     None,
                                     True)
        else:
            if len(vals) != 3 and context is undefined:
                raise ConfigError(_('ip_network needs an IP, a network and a netmask'))
            if len(vals) != 3 or None in vals:
                return
            ip, network, netmask = vals
            if ip_interface(ip) not in ip_network('{0}/{1}'.format(network,
                                                                   netmask)):
                msg = _('"{4}" is not in network "{0}"/"{1}" ("{2}"/"{3}")')
                raise ValueError(msg.format(network,
                                            netmask,
                                            opts[1].impl_get_display_name(),
                                            opts[2].impl_get_display_name(),
                                            ip))
            # test if ip is not network/broadcast IP
            opts[2]._cons_ip_netmask(current_opt,
                                     (opts[2], opts[0]),
                                     (netmask, ip),
                                     warnings_only,
                                     context)
