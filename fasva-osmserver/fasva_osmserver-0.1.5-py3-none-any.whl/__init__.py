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

CONFIG_SECTION_OSMSERVER = "osmserver"
CONFIG_SECTION_OSMSERVER_OPTION_HOST = "host"
CONFIG_SECTION_OSMSERVER_OPTION_PORT = "port"
CONFIG_SECTION_OSMSERVER_OPTION_INTERPRETER = "interpreter"
CONFIG_SECTION_OSMSERVER_OPTION_INTERVAL = "interval"

CONFIG_SECTION_OSMSERVER_OPTION_API_HOST = "api-host"
CONFIG_SECTION_OSMSERVER_OPTION_API_USER = "api-user"
CONFIG_SECTION_OSMSERVER_OPTION_API_PASSWORD = "api-password"

CONFIG_MAPPING = {
    CONFIG_SECTION_OSMSERVER: [
        CONFIG_SECTION_OSMSERVER_OPTION_INTERPRETER,
        CONFIG_SECTION_OSMSERVER_OPTION_API_HOST,
        CONFIG_SECTION_OSMSERVER_OPTION_API_USER,
        CONFIG_SECTION_OSMSERVER_OPTION_API_PASSWORD
    ]
}
