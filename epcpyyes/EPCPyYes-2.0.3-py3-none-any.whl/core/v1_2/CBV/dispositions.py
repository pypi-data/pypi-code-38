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

from enum import Enum

class Disposition(Enum):
    '''
    CBV Disposition values as defined in section 7.2 of the standard.
    '''
    active = 'urn:epcglobal:cbv:disp:active'
    container_closed = 'urn:epcglobal:cbv:disp:container_closed'
    damaged = 'urn:epcglobal:cbv:disp:damaged'
    destroyed = 'urn:epcglobal:cbv:disp:destroyed'
    dispensed = 'urn:epcglobal:cbv:disp:dispensed'
    disposed = 'urn:epcglobal:cbv:disp:disposed'
    encoded = 'urn:epcglobal:cbv:disp:encoded'
    expired = 'urn:epcglobal:cbv:disp:expired'
    in_progress = 'urn:epcglobal:cbv:disp:in_progress'
    in_transit = 'urn:epcglobal:cbv:disp:in_transit'
    inactive = 'urn:epcglobal:cbv:disp:inactive'
    no_pedigree_match = 'urn:epcglobal:cbv:disp:no_pedigree_match'
    non_sellable_other = 'urn:epcglobal:cbv:disp:non_sellable_other'
    partially_dispensed = 'urn:epcglobal:cbv:disp:partially_dispensed'
    recalled = 'urn:epcglobal:cbv:disp:recalled'
    reserved = 'urn:epcglobal:cbv:disp:reserved'
    retail_sold = 'urn:epcglobal:cbv:disp:retail_sold'
    returned = 'urn:epcglobal:cbv:disp:returned'
    sellable_accessible = 'urn:epcglobal:cbv:disp:sellable_accessible'
    sellable_not_accessible = 'urn:epcglobal:cbv:disp:sellable_not_accessible'
    stolen = 'urn:epcglobal:cbv:disp:stolen'
    unknown = 'urn:epcglobal:cbv:disp:unknown'

    def __str__(self):
        return self.value