# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import String, Selection, URL
import logging

logger = logging.getLogger(__name__)


@Declarations.register(Declarations.Model.Bus)
class Profile:
    name = String(primary_key=True, unique=True, nullable=False)
    description = String()
    url = URL(nullable=False)
    state = Selection(
        selections={
            'connected': 'Connected',
            'disconnected': 'Disconnected'
        },
        default='disconnected', nullable=False
    )
