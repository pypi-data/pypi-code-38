# This file is a part of the AnyBlok / Bus project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration
import os


Configuration.add_application_properties('createdb', ['bus'])
Configuration.add_application_properties('updatedb', ['bus'])
Configuration.add_application_properties('nose', ['bus'])
Configuration.add_application_properties('interpreter', ['bus'])
Configuration.add_application_properties('default', ['bus'])

Configuration.add_application_properties('pyramid', ['bus'])
Configuration.add_application_properties('gunicorn', ['bus'],
                                         add_default_group=False)


@Configuration.add(
    'bus', label="Bus - options", must_be_loaded_by_unittest=True
)
def define_bus_broker(group):
    group.add_argument('--bus-profile',
                       default=os.environ.get('ANYBLOK_BUS_PROFILE'),
                       help="Profile to use")
    group.add_argument('--bus-processes', type=int,
                       default=os.environ.get('ANYBLOK_BUS_PROCESSES', 4),
                       help="Number of process")
