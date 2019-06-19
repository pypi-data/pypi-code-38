###############################################################################
# (c) Copyright 2017 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Package initialization
"""

from lbmessaging.exchanges.Common import get_connection

# Priority management
##################################

# Levels
EMERGENCY = "EMERGENCY"
HIGH = "HIGH"
NORMAL = "NORMAL"
LOW = "LOW"

# Their mappings to actual values
# We add an extra level for the sake of the priority computation
_levels = [LOW, NORMAL, HIGH, EMERGENCY, "END"]
_values = [0, 128, 200, 255, 256]
_map = dict(zip(_levels, _values))


def priority(level, weight=0.0):
    """
    :param level: The priority level for the message, should be one of the official levels
    :param weight: important withn the range (float within 0 and 1)
    :return: the priority for the message translated to the range known by RabbitMQ queues (0-255)
    """

    if (level not in _levels):
        raise Exception("Unknown level")

    # +1 works as we have an extra / undeclared level
    nextlevel = _levels[_levels.index(level) + 1]
    low_priority = _map[level]
    high_priority = _map[nextlevel] - 1

    # map linearly to the range...
    return int(low_priority + weight * float(high_priority - low_priority))
