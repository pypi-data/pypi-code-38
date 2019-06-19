# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import logging

UNIVERSAL = 60


logging.addLevelName(UNIVERSAL, 'UNIVERSAL')


def setup_core_loglevel(level):
    setup_basic_logger('core', level)


def setup_node_loglevel(level):
    setup_basic_logger('node', level)


def setup_basic_logger(name, level):
    levels = [UNIVERSAL,
              logging.CRITICAL,
              logging.ERROR,
              logging.WARNING,
              logging.INFO,
              logging.DEBUG]

    logging_level = levels[level]

    logger = logging.getLogger(name)
    logger.setLevel(logging_level)


def setup_loglevel(core_level, node_level):
    setup_core_loglevel(core_level)
    setup_node_loglevel(node_level)

    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(logging.BASIC_FORMAT)

    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)

