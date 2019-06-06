#
# Copyright (c) 2018 - 2019, Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict
from zb_cli_wrapper.nrf_dev_map.case_insensitive_dict import CaseInsensitiveDict


Vendor = Enum('Vendor', ['Segger', 'CDC'])
ALL_VENDORS = [v for v in Vendor]
MBED_ID_LENGTH = 48

class ComPortMapAbstract(ABC):
    @classmethod
    @abstractmethod
    def get_registered_boards_ids(cls, vendors) -> 'List[str]':
        '''
        Get list of ids for devices registered in the system
        :param: vendors: One or multiple vendors
        :return: a list like ['683756583', '683011151'] or
                             ['683512372', 'F8C8284B1C1E', '1102000044203120334c3941313034203431303397969903']
        '''
        pass #To be implemented in descendants

    @classmethod
    def get_com_ports_by_id(cls, board_id, vendors=ALL_VENDORS):
        '''
        Get COM port(s) for device with given id
        :param vendors: One or multiple vendors
        :return: a dict like {0: 'COM4', '00': 'COM4'} or
                             {0: 'COM10', 1: 'COM8', 2: 'COM9', '00': 'COM10', '02': 'COM8', '04': 'COM9'}.
        Note that the dict is double-indexed by integer and two-digit value which corresponds to Multiple Interface
        '''
        id_lower = board_id.lower()
        return next((v for k, v in cls.get_iter(vendors) if k.lower() == id_lower),
                    cls.empty_com_ports_dict())

    @classmethod
    def get(cls, vendors):
        '''
        Get full device id - COM port mapping
        :param vendors: One or multiple vendors
        :return: a dict like
        {
            '683756583': {0: 'COM8', '00': 'COM8'},
            '960014618': {0: 'COM10', 1: 'COM8', 2: 'COM9', '00': 'COM10', '02': 'COM8', '04': 'COM9'},
            1102000044203120334c3941313034203431303397969903': {0: 'COM5', '01': 'COM5'}
        }
        '''
        result = CaseInsensitiveDict()
        for board_id, com_ports in cls.get_iter(vendors):
            result[board_id] = com_ports
        return result

    @classmethod
    @abstractmethod
    def get_iter(cls, vendors) -> 'Iterator[Tuple[str, dict]]':
        '''
        Similar to `get`, but returns generator
        '''
        pass #To be implemented in descendants

    @classmethod
    def empty_com_ports_dict(cls):
        ''' Empty dict for when no com ports were found (yet) '''
        return defaultdict(type(None))
