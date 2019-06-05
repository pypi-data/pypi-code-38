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


class BusinessSteps(Enum):
    '''
    CVB 1.2 Business Steps as defined in section 7.1 of the standard.
    '''
    accepting = 'urn:epcglobal:cbv:bizstep:accepting'
    arriving = 'urn:epcglobal:cbv:bizstep:arriving'
    assembling = 'urn:epcglobal:cbv:bizstep:assembling'
    collecting = 'urn:epcglobal:cbv:bizstep:collecting'
    commissioning = 'urn:epcglobal:cbv:bizstep:commissioning'
    consigning = 'urn:epcglobal:cbv:bizstep:consigning'
    creating_class_instance = 'urn:epcglobal:cbv:bizstep:creating_class_instance'
    cycle_counting = 'urn:epcglobal:cbv:bizstep:cycle_counting'
    decommissioning = 'urn:epcglobal:cbv:bizstep:decommissioning'
    departing = 'urn:epcglobal:cbv:bizstep:departing'
    destroying = 'urn:epcglobal:cbv:bizstep:destroying'
    disassembling = 'urn:epcglobal:cbv:bizstep:disassembling'
    dispensing = 'urn:epcglobal:cbv:bizstep:dispensing'
    entering_exit = 'urn:epcglobal:cbv:bizstep:entering_exit'
    ingholding = 'urn:epcglobal:cbv:bizstep:ingholding'
    inspecting = 'urn:epcglobal:cbv:bizstep:inspecting'
    installing = 'urn:epcglobal:cbv:bizstep:installing'
    killing = 'urn:epcglobal:cbv:bizstep:killing'
    loading = 'urn:epcglobal:cbv:bizstep:loading'
    other = 'urn:epcglobal:cbv:bizstep:other'
    packing = 'urn:epcglobal:cbv:bizstep:packing'
    picking = 'urn:epcglobal:cbv:bizstep:picking'
    receiving = 'urn:epcglobal:cbv:bizstep:receiving'
    removing = 'urn:epcglobal:cbv:bizstep:removing'
    repackaging = 'urn:epcglobal:cbv:bizstep:repackaging'
    repairing = 'urn:epcglobal:cbv:bizstep:repairing'
    replacing = 'urn:epcglobal:cbv:bizstep:replacing'
    reserving = 'urn:epcglobal:cbv:bizstep:reserving'
    retail_selling = 'urn:epcglobal:cbv:bizstep:retail_selling'
    shipping = 'urn:epcglobal:cbv:bizstep:shipping'
    staging_outbound = 'urn:epcglobal:cbv:bizstep:staging_outbound'
    stock_taking = 'urn:epcglobal:cbv:bizstep:stock_taking'
    stocking = 'urn:epcglobal:cbv:bizstep:stocking'
    storing = 'urn:epcglobal:cbv:bizstep:storing'
    transporting = 'urn:epcglobal:cbv:bizstep:transporting'
    unloading = 'urn:epcglobal:cbv:bizstep:unloading'
    unpacking = 'urn:epcglobal:cbv:bizstep:unpacking'
    void_shipping = 'urn:epcglobal:cbv:bizstep:void_shipping'

    def __str__(self):
        return self.value