# -*- coding: utf-8 -*-

"""package iopy
author    Benoit Dubois
copyright FEMTO ENGINEERING
license   GPL v3.0+
brief     Basic API to handle Cypress’s EZ-USB® FX2LP (TM) type device.
"""

import os
import time
import logging
import usb.core
import usb.util


#==============================================================================
class Fx2Core(object):
    """Core class for FX2 USB driver.
    """

    def __init__(self):
        super().__init__()
        self._dev = None
        self._ep_in = None
        self._ep_out = None
        self._ep_dat_in = None
        self._ep_dat_out = None

    def is_connected(self):
        if self._dev is None:
            return False
        return True

    def disconnect(self):
        if self._dev is not None:
            ##del(self._dev)
            #self._dev = None
            pass

    def connect(self, vendor_id, product_id):
        """Set an object representing our device (usb.core.Device).
        :param vendor_id: identification number of vendor (int)
        :param product_id: identification number of product (int)
        :returns: True if connection is Ok else returns False (bool)
        """
        # Find our device
        self._dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        # Was it found?
        if self._dev is None:
            logging.warning("Device not found")
            return False
        # Detach the kernel driver if it is active
        if self._dev.is_kernel_driver_active(0):
            try:
                self._dev.detach_kernel_driver(0)
            except usb.core.USBError as ex:
                logging.critical("Could not detach kernel driver: %r", ex)
                return False
        return True

    def config(self, config_id, interface_id, alt_interface_id, out_ep_id, \
               in_ep_id, out_dat_ep_id, in_dat_ep_id):
        """Configure device and get endpoint instance.
        Endpoint Address description:
        - Bits 0..3 Endpoint Number.
        - Bits 4..6 Reserved. Set to Zero
        - Bits 7 Direction 0 = Out, 1 = In (Ignored for Control Endpoints)
        Example: address = 129 = (81)8 = (1000 0001)2
                 -> Direction: In, Number: 1
        :param config_id:
        ...
        :returns: None
        """
        try:
            self._dev.set_configuration(config_id)
        except usb.core.USBError as ex:
            logging.critical("USB error during dev configuration: %r", ex)
            raise
        except Exception as ex:
            logging.critical("Could not set interface configuration: %r", ex)
            raise
        self._dev.reset()
        # Set interface
        try:
            self._dev.set_interface_altsetting(interface=interface_id, 
                                        alternate_setting=alt_interface_id)
        except usb.core.USBError as ex:
            logging.critical("USB error during interface altsetting: %r", ex)
            raise
        except Exception as ex:
            logging.critical("Error during interface altsetting: %r", ex)
            raise
        # Get endpoint instances
        try:
            self._ep_out = self._dev[config_id-1] \
                [(interface_id, alt_interface_id)][out_ep_id]
            self._ep_in = self._dev[config_id-1] \
                [(interface_id, alt_interface_id)][in_ep_id]
            self._ep_dat_out = self._dev[config_id-1][(interface_id, \
                                            alt_interface_id)][out_dat_ep_id]
            self._ep_dat_in = self._dev[config_id-1][(interface_id, \
                                        alt_interface_id)][in_dat_ep_id]
        except usb.core.USBError as ex:
            logging.critical("Could not set endpoint setting: %r", ex)
        logging.debug("USB interface succefuly configured")

    @staticmethod
    def load_firmware(fw_file, vendor_id, product_id):
        """Load firmware in FX2 device
        The vendor_id and product_id are used to determine the bus and the
        device number.
        :param vendor_id: as it say (int).
        :param product_id: as it say (int).
        :param fw_file: firmware hexfile for FX2 device (str).
        :returns: None
        """
        from subprocess import call

        if fw_file is None:
            logging.critical("No firmware file given")
            raise ValueError
        fw_file = os.path.expanduser(fw_file)
        if os.path.exists(fw_file) is False:
            logging.critical("Firmware loading failed, firmware file not found")
            raise ValueError
        # Find our device
        dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if dev is None:
            logging.error("Firmware loading failed, device with vendor id %s"
                          " and product id %s is not found",
                          vendor_id, product_id)
            raise ValueError
        bus = dev.bus
        address = dev.address
        dev_path = "/dev/bus/usb/{:03}/{:03}".format(bus, address)
        if dev_path is None:
            logging.error("Firmware loading failed, firmware path '%s', "
                          + "not found", dev_path)
            raise IOError
        fxload_arg = " -t fx2 -D " + dev_path + " -I " + fw_file
        # Note: fxload seems to do not return 0 when succeeded.
        # TODO: handle error.
        call("/sbin/fxload" + fxload_arg, shell=True)
        time.sleep(1)
        logging.debug("Firmware loading succeeded")

    def write_ctrl(self, msg):
        """Write raw data on control endpoint.
        The method don't take care about meaning of msg.
        :param msg: message to write to device (sequence like type convertible
                    to array type of int cf usb.core.device.write()).
        :returns: number of bytes sent (int).
        """
        try:
            nb = self._ep_out.write(msg)
        except usb.core.USBError as ex:
            logging.error("Could not write data: %r", ex)
            return 0
        return nb

    def read_ctrl(self):
        """Read raw dat on control endpointa.
        :returns: Received bytes (list of ?).
        """
        # Collect data
        data = []
        try:
            data = self._ep_in.read(self._ep_dat_in.wMaxPacketSize)
        except usb.core.USBError as ex:
            logging.error("Could not read data: %r", ex)
        return data

    def write(self, msg):
        """Write raw data.
        The method don't take care about meaning of msg.
        Write on the DDS board is handled by a FX2 device (USB interface).
        A write cycle on the FX2 device is divided in two parts:
        - init message writed to main endpoint (EP0),
        - real message writed to 'data' endpoint (EP4).
        Writing on the USB bus is transparent: you transmit each bit in order.
        Writing on the USB bus consists in filling the write function (usb.core)
        with a list of binary values.
        :param msg: message to write to device (sequence like type convertible
                    to array type of int cf usb.core.device.write()).
        :returns: number of bytes sent (int).
        """
        try:
            nb = self._ep_dat_out.write(msg)
        except usb.core.USBError as ex:
            logging.error("Could not write data: %r", ex)
            return 0
        return nb

    def read(self):
        """Read raw data.
        The method don't take care about meaning of data.
        :returns: Received bytes (list of ?).
        """
        # Collect data
        data = []
        try:
            data = self._ep_dat_in.read(self._ep_dat_in.wMaxPacketSize)
        except usb.core.USBError as ex:
            logging.error("Could not read data: %r", ex)
        return data
