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
from ipaddress import ip_address
from ..setting import undefined, Undefined, OptionBag
from ..i18n import _
from .option import Option
from .ipoption import IPOption


class DomainnameOption(IPOption):
    """represents the choice of a domain name
    netbios: for MS domain
    hostname: to identify the device
    domainname:
    fqdn: with tld, not supported yet
    """
    __slots__ = tuple()
    _type = 'domainname'
    _display_name = _('domain name')

    def __init__(self,
                 name,
                 doc,
                 default=None,
                 default_multi=None,
                 requires=None,
                 multi: bool=False,
                 callback=None,
                 callback_params=None,
                 validator=None,
                 validator_params=None,
                 properties=None,
                 allow_ip: bool=False,
                 cidr: bool=False,
                 type_: str='domainname',
                 warnings_only: bool=False,
                 allow_without_dot=False) -> None:

        if type_ not in ['netbios', 'hostname', 'domainname']:
            raise ValueError(_('unknown type_ {0} for hostname').format(type_))
        extra = {'_dom_type': type_}
        if allow_ip not in [True, False]:
            raise ValueError(_('allow_ip must be a boolean'))
        if allow_without_dot not in [True, False]:
            raise ValueError(_('allow_without_dot must be a boolean'))
        extra['_allow_ip'] = allow_ip
        extra['_allow_without_dot'] = allow_without_dot
        if type_ == 'domainname':
            if allow_without_dot:
                min_time = 0
            else:
                min_time = 1
            regexp = r'((?!-)[a-z0-9-]{{{1},{0}}}\.){{{1},}}[a-z0-9-]{{1,{0}}}'.format(self._get_len(type_), min_time)
        else:
            regexp = r'((?!-)[a-z0-9-]{{1,{0}}})'.format(self._get_len(type_))
        if allow_ip:
            if not cidr:
                regexp = r'^(?:{0}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){{3}}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)))$'.format(regexp)
            else:
                regexp = r'^(?:{0}|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){{3}}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/[0-9][0-9]))$'.format(regexp)
        else:
            regexp = r'^{0}$'.format(regexp)
        extra['_domain_re'] = re.compile(regexp)
        extra['_has_upper'] = re.compile('[A-Z]')

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
                         cidr=cidr,
                         _extra=extra)

    def _get_len(self, type_):
        if type_ == 'netbios':
            return 15
        else:
            return 63

    def _validate(self,
                  value: str,
                  option_bag: OptionBag,
                  current_opt: Option=Undefined) -> None:
        def _valid_length(val):
            if len(val) < 1:
                raise ValueError(_("invalid length (min 1)"))
            if len(val) > part_name_length:
                raise ValueError(_("invalid length (max {0})"
                                    "").format(part_name_length))

        if not isinstance(value, str):
            raise ValueError(_('invalid string'))
        try:
            ip_address(value)
        except ValueError:
            pass
        else:
            if self.impl_get_extra('_allow_ip') is False:
                raise ValueError(_('must not be an IP'))
            # it's an IP so validate with IPOption
            return super()._validate(value, option_bag, current_opt)
        part_name_length = self._get_len(self.impl_get_extra('_dom_type'))
        if self.impl_get_extra('_dom_type') == 'domainname':
            if not self.impl_get_extra('_allow_without_dot') and not "." in value:
                raise ValueError(_("must have dot"))
            if len(value) > 255:
                raise ValueError(_("invalid length (max 255)"))
            for dom in value.split('.'):
                _valid_length(dom)
        else:
            _valid_length(value)

    def _second_level_validation(self, value, warnings_only):
        if self.impl_get_extra('_has_upper').search(value):
            raise ValueError(_('some characters are uppercase'))
        if not self.impl_get_extra('_domain_re').search(value):
            if warnings_only:
                raise ValueError(_('some characters may cause problems'))
            else:
                raise ValueError()
