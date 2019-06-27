# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2019
license   GPL v3.0+
brief     USB utilities.
"""

import usb.core
import usb.util
import usb.control


#==============================================================================
def to_le16(byte1, byte2):
    """Utility for converting two adjacent bytes, assumed to be in order, to a
    *signed* 16-bit little-endian value (stored as a Python integer, which is
    arbitrary precision)
    """
    val = 0
    if byte2 & 0x80:
        val = -32768
        byte2 = byte2 & 0x7f
    val += (byte2 << 8) + byte1
    return val


#==============================================================================
def print_usb_dev_cfg(dev):
    """Print usb configuration interface.
    :param dev: USB device of attention
    :returns: None
    """
    print("Device bus:", dev.bus)
    print("Device address:", dev.address)
    for cfg in dev:
        print("Config_value:", cfg.bConfigurationValue)
        print("Config_length:", cfg.wTotalLength)
        for intf in cfg:
            print("  Interface_number:", intf.bInterfaceNumber)
            print("  Interface_alternate:", intf.bAlternateSetting)
            print("  Interface_ep_total_number:", intf.bNumEndpoints)
            for ep in intf:
                print("    EP_address:", ep.bEndpointAddress)
                print("      MaxSize:", ep.wMaxPacketSize)
                print("      Lenght:", ep.bLength)
                print("      Interval:", ep.bInterval)
                if usb.util.endpoint_direction(ep.bEndpointAddress) == 0:
                    print("      direction: ENDPOINT_OUT")
                else:
                    print("      direction: ENDPOINT_IN")
                if usb.util.endpoint_type(ep.bmAttributes) == 0:
                    print("      type: CTRL")
                elif usb.util.endpoint_type(ep.bmAttributes) == 1:
                    print("      type: ISO")
                elif usb.util.endpoint_type(ep.bmAttributes) == 2:
                    print("      type: BULK")
                else:
                    print("      type: INTR")


#==============================================================================
def print_usb_cfg(id_vendor, id_product):
    """Print usb configuration interface.
    :param id_vendor: Vendor identification index (int)
    :param id_product: Product identification index (int)
    :returns: None
    """
    # Find our device
    dev = usb.core.find(idVendor=id_vendor, idProduct=id_product)
    # Was it found?
    if dev is None:
        raise ValueError('Devices not found')
    # Print usb interface configuration
    print_usb_dev_cfg(dev)
