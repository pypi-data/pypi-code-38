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


class BusinessTransactionType(Enum):
    '''
    Business Transaction Types as defined in section 7.3 of the standard.
    '''
    Bill_Of_Lading = 'urn:epcglobal:cbv:btt:bol'
    Despatch_Advice = 'urn:epcglobal:cbv:btt:desadv'
    Invoice = 'urn:epcglobal:cbv:btt:inv'
    Pedigree = 'urn:epcglobal:cbv:btt:pedigree'
    Purchase_Order = 'urn:epcglobal:cbv:btt:po'
    Purchase_Order_Confirmation = 'urn:epcglobal:cbv:btt:poc'
    Production_Order = 'urn:epcglobal:cbv:btt:prodorder'
    Receiving_Advice = 'urn:epcglobal:cbv:btt:recadv'
    Return_Merchandise_Authorization = 'urn:epcglobal:cbv:btt:rma'

    def __str__(self):
        return self.value