# Copyright (C) 2012-2019 Team tiramisu (see AUTHORS for all contributors)
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
"""Configuration management library written in python
"""
from .function import Params, ParamOption, ParamValue, ParamContext, \
                      tiramisu_copy, calc_value
from .option import *
from .error import APIError
from .api import Config, MetaConfig, GroupConfig, MixConfig
from .option import __all__ as all_options
from .setting import owners, undefined
from .storage import default_storage, Storage, list_sessions, \
                     delete_session


allfuncs = ['Params',
            'ParamOption', 
            'ParamValue',
            'ParamContext',
            'MetaConfig',
            'MixConfig',
            'GroupConfig',
            'Config',
            'APIError',
            'undefined',
            'default_storage',
            'Storage',
            'list_sessions',
            'delete_session',
            'tiramisu_copy',
            'calc_value']
allfuncs.extend(all_options)
del(all_options)
__all__ = tuple(allfuncs)
del(allfuncs)
__version__ = "3.0rc7"
