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


class Bus(Blok):
    """Add bus configuration in AnyBlok"""

    version = version
    required = ['anyblok-core']
    author = 'Suzanne Jean-Sébastien'

    @classmethod
    def import_declaration_module(cls):
        from . import bus  # noqa
        from . import profile  # noqa
        from . import message  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import bus
        reload(bus)
        from . import profile
        reload(profile)
        from . import message
        reload(message)
