# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok_bus.release import version


class BusTraces(Blok):
    """Save Trace from bus in database"""

    version = version
    required = ['anyblok-core', 'bus']
    author = 'Suzanne Jean-Sébastien'

    @classmethod
    def import_declaration_module(cls):
        from . import trace  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import trace
        reload(trace)
