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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.
"""

A series of Django two-tuple choices for models and also contains
an EventType enum for EPCIS event types to ensure that the code and the
choices always match up accurately.

"""


from enum import Enum

ACTION_CHOICES = (
    ('ADD', 'Add'),
    ('OBSERVE', 'Observe'),
    ('DELETE', 'Delete')
)

EVENT_TYPE_CHOICES = (
    ('ag', 'Aggregation'),
    ('ob', 'Object'),
    ('tx', 'Transaction'),
    ('tf', 'Transformation')
)

class EventTypeChoicesEnum(Enum):
    '''
    Helper used to avoid any errors when using the choices outside of models.
    '''
    AGGREGATION = 'ag'
    OBJECT = 'ob'
    TRANSACTION = 'tx'
    TRANSFORMATION = 'tf'
