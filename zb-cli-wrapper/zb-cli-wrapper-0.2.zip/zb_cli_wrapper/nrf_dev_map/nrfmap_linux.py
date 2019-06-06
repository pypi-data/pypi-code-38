#
# Copyright (c) 2016 - 2019, Nordic Semiconductor ASA
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

import os, re
import logging
import itertools
from pathlib import Path
from zb_cli_wrapper.nrf_dev_map.nrfmap_common import Vendor, ALL_VENDORS, ComPortMapAbstract


class ComPortMapLinux(ComPortMapAbstract):
    ''' See ComPortMapAbstract for public functions documentation '''

    VENDOR_NAMES = {
        Vendor.Segger: 'usb-SEGGER_J-Link_',
        Vendor.CDC: 'usb-Nordic_Semiconductor_.*_' #note: regex here
    }

    @classmethod
    def get_registered_boards_ids(cls, vendors):
        return [board_id for board_id, _ in cls._create_com_port_map_gen(vendors)]

    @classmethod
    def get_iter(cls, vendors):
        yield from cls._create_com_port_map_gen(vendors)

    @classmethod
    def dev_usb_iter(cls, vendors=ALL_VENDORS):
        '''
        Get generator for board id - usb device path mapping
        :param vendors: One or multiple vendors
        :return: pairs like '683756583': '/dev/bus/usb/002/011'
        '''
        for board_id, com_ports in cls._create_com_port_map_gen(vendors):
            sys_class_tty = Path('/sys/class/tty') / Path(com_ports[0]).name # /sys/class/tty/ttyACM0
            sys_devices_usb_bus_port = sys_class_tty.resolve() / '../../..'  # /sys/devices/pci0000:00/0000:00:0b.0/usb1/1-2
            busnum = (sys_devices_usb_bus_port / 'busnum').read_text() # NB: only since Python 3.5
            busnum = int(busnum)
            devnum = (sys_devices_usb_bus_port / 'devnum').read_text()
            devnum = int(devnum)
            yield board_id, '/dev/bus/usb/%03d/%03d' % (busnum, devnum)

    @classmethod
    def _create_com_port_map_flat_gen(cls, vendors):
        if not isinstance(vendors, list):
            vendors = [vendors]
        regex = re.compile('({vendor_names})([\d\w]+)-if([\w]+)'.format(
            vendor_names='|'.join(cls.VENDOR_NAMES[v] for v in vendors)))

        snrs_d = []
        DEVPATH = '/dev/serial/by-id/'
        try:
            for dev in sorted(os.listdir(DEVPATH)):
                match = regex.match(dev)
                if match:
                    vendor_name, board_id, multiple_interface = match.groups()
                    if vendor_name == cls.VENDOR_NAMES[Vendor.Segger]:
                        board_id = board_id.lstrip('0')
                    com_port = os.path.realpath(DEVPATH + dev) #follow symlink to get target path
                    snrs_d.append((board_id, multiple_interface, com_port))
                    yield board_id, multiple_interface, com_port
        except IOError as e:
            logging.debug('ComPortMap IOError: %s', str(e))

    @classmethod
    def _create_com_port_map_gen(cls, vendors):
        # Convert flat mapping (multiple_interface - com_port) to com_ports dict via
        # grouping by board_tuple[0] (which is board_id)
        for board_id, com_port_tuple in itertools.groupby(cls._create_com_port_map_flat_gen(vendors), lambda board_tuple: board_tuple[0]):
            com_ports_by_index = {}
            com_ports_by_mi = {}
            for index, (_, multiple_interface, com_port) in enumerate(com_port_tuple, 0):
                com_ports_by_index[index] = com_ports_by_mi[multiple_interface] = com_port
            com_ports = cls.empty_com_ports_dict()
            com_ports.update(com_ports_by_index)
            com_ports.update(com_ports_by_mi)
            yield board_id, com_ports
