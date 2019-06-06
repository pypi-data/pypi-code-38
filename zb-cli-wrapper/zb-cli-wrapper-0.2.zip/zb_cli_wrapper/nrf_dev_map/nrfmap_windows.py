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

import re
import winreg
import logging
import traceback
from collections import namedtuple
from zb_cli_wrapper.nrf_dev_map.nrfmap_common import Vendor, ComPortMapAbstract, MBED_ID_LENGTH

# Serial number can be SEGGER (eg. 683512372) or CDC serial number (eg. F8C8284B1C1E)
UsbId = namedtuple('UsbId', 'Id SerialNumber')


class ComPortMapWindows(ComPortMapAbstract):
    ''' See ComPortMapAbstract for public functions documentation '''

    VENDOR_IDS = {
        Vendor.Segger: '1366',
        Vendor.CDC: '1915'
    }
    ''' USB VID hex values '''

    @classmethod
    def get_registered_boards_ids(cls, vendors):
        return [board_id for board_id, _ in cls._get_usb_id_for_serial_num_gen(vendors)]

    @classmethod
    def get_iter(cls, vendors):
        usb_id_for_serial_num = cls._get_usb_id_for_serial_num_gen(vendors)
        yield from cls._create_com_port_map_gen(usb_id_for_serial_num)

    @classmethod
    def _get_usb_id_for_serial_num_gen(cls, vendors):
        """
        :return: For example '683512372', UsbId(Id='VID_1366&PID_1015', SerialNumber='000683512372')
        """
        if not isinstance(vendors, list):
            vendors = [vendors]
        regex = re.compile(r'USB\\VID_({vendor_ids})&PID_[\w]+\\([\w]+)'.format(
            vendor_ids='|'.join(cls.VENDOR_IDS[v] for v in vendors)))

        enum_usbccgp = r'SYSTEM\CurrentControlSet\Services\usbccgp\Enum'
        enum_mbedComposite = r'SYSTEM\CurrentControlSet\Services\mbedComposite\Enum'

        def get_device(enum_key):
            number_of_values = winreg.QueryInfoKey(enum_key)[1]
            for i in range(number_of_values):
                value_name, value_data, _ = winreg.EnumValue(enum_key, i)
                if value_name.isdigit():  # device 0, 1, 2...
                    m = regex.match(value_data)
                    if m:
                        id_parts = value_data.split('\\')  # ['USB', 'VID_XXXX&PID_XXXX', 'SERIAL_NUMBER']
                        vid, board_id = m.groups()
                        if vid == cls.VENDOR_IDS[Vendor.Segger]:
                            board_id = board_id.lstrip('0')
                        yield board_id, UsbId(id_parts[1], id_parts[2])

        for enum in [enum_usbccgp, enum_mbedComposite]:
            try:
                enum_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, enum)
                yield from get_device(enum_key)
            except OSError:
                logging.debug("Serial service unavailible: {service}".format(service=enum))

    @classmethod
    def _create_com_port_map_gen(cls, usb_id_for_serial):
        for snr, usb_id in usb_id_for_serial:
            pid = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 'SYSTEM\\CurrentControlSet\\Enum\\USB\\' + usb_id.Id + '\\' +
                                 usb_id.SerialNumber)
            try:
                parent_id_prefix = winreg.QueryValueEx(pid, "ParentIdPrefix")[0]
            except OSError:
                # Assume the ParentIdPrefix is the snr (From the mbedSerial_x64 driver)
                parent_id_prefix = usb_id.SerialNumber

            com_ports_by_index = {}
            com_ports_by_mi = {}
            com_ports_count = 0
            key_usb = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Enum\USB')
            n_subkeys, _, _ = winreg.QueryInfoKey(key_usb)
            for i in range(n_subkeys):
                key_name = winreg.EnumKey(key_usb, i)
                m = re.match(usb_id.Id + '&MI_([\w]+)', key_name)
                if m:
                    (multiple_interface, ) = m.groups()
                    comPortEntryKey = 'SYSTEM\\CurrentControlSet\\Enum\\USB\\' + usb_id.Id + \
                              "&MI_" + multiple_interface + "\\" + parent_id_prefix + \
                                      ("&00" + multiple_interface if len(parent_id_prefix) < MBED_ID_LENGTH else "")
                    # If parent_id_prefix is less than 48 chars it was procured from usbccgp rather than
                    # mbedCompositeEnum. usbccgp keeps the MI in the signature
                    try:
                        comPortEntry = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, comPortEntryKey)
                        comPortValue = str(winreg.QueryValueEx(comPortEntry, "FriendlyName")[0])
                        com_ports_by_index[com_ports_count] = com_ports_by_mi[multiple_interface] = \
                            comPortValue[comPortValue.index('(') + 1: comPortValue.index(')')]
                        com_ports_count += 1
                    except OSError:
                        logging.debug('No COM port found for %s (%s)', comPortEntryKey, traceback.format_exc())
                    except ValueError:
                        logging.debug('comPortValue.index: COM port not found in "%s"', comPortValue)
            com_ports = cls.empty_com_ports_dict()
            com_ports.update(com_ports_by_index)
            com_ports.update(com_ports_by_mi)
            yield snr, com_ports
