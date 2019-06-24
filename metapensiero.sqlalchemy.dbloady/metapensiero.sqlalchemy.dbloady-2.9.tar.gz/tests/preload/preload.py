# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- Sample preload script
# :Created:   gio 14 gen 2016 11:35:38 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Lele Gaifax
#

import datetime, re

from ruamel import yaml

def time_constructor(loader, node):
    value = loader.construct_scalar(node)
    if value.startswith('T'):
        value = value[1:]
    parts = map(int, value.split(':'))
    return datetime.time(*parts)

yaml.add_constructor('!time', time_constructor)
yaml.add_implicit_resolver('!time', re.compile(r'^T?\d{2}:\d{2}(:\d{2})?$'), ['T'])
