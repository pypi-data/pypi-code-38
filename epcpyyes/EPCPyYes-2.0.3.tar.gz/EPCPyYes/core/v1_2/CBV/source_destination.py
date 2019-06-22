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
# Copyright 2018 Rob Magee.  All rights reserved.

from enum import Enum

class SourceDestinationTypes(Enum):
    '''
    Source Destination Types as defined in section 7.4 of the document.
    '''
    owning_party = 'urn:epcglobal:cbv:sdt:owning_party'
    possessing_party =  'urn:epcglobal:cbv:sdt:possessing_party'
    location = 'urn:epcglobal:cbv:sdt:location'

    def __str__(self):
        return self.value