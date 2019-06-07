# -*- tab-width: 4; encoding: utf-8; -*-
# ex: set tabstop=4 expandtab:
# Copyright (c) 2016-2018 by Lars Klitzke, Lars.Klitzke@hs-emden-leer.de.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import random

import aiohttp

from osmserver import CONFIG_SECTION_OSMSERVER_OPTION_API_HOST, CONFIG_SECTION_OSMSERVER_OPTION_API_USER, \
    CONFIG_SECTION_OSMSERVER_OPTION_API_PASSWORD


async def module_states(**kwargs):
    """
    Query the RESTfull API of the FASva server to retrieve all drives.

    Keyword Args:
        api-host (str): The host of the FASva-RESTfull API
        api-user (int): User name for basic authentication
        api-password (str):  User password for basic authentication

    Returns:

    """
    params = {
        'url': kwargs.get(CONFIG_SECTION_OSMSERVER_OPTION_API_HOST) + "/drive",
        'auth': aiohttp.BasicAuth(login=kwargs.get(CONFIG_SECTION_OSMSERVER_OPTION_API_USER),
                                  password=kwargs.get(CONFIG_SECTION_OSMSERVER_OPTION_API_PASSWORD)),
        'verify_ssl': False
    }

    state = {}

    async with aiohttp.ClientSession() as session:

        async with session.get(**params) as response:

            drives = [d['name'] for d in await response.json()]

            random.shuffle(drives)

            for prop in ['processed', 'current', 'unprocessed', 'failed']:

                if not drives:
                    state[prop] = []
                try:
                    state[prop] = random.sample(drives, random.randint(1, len(drives)))
                except ValueError:
                    state[prop] = []

                [drives.remove(d) for d in state[prop]]

    return state

