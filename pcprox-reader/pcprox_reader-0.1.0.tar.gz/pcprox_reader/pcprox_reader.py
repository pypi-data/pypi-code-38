# -*- coding: utf-8 -*-
""" 
    Main module.
    Forked and adapted from https://github.com/sawahashi3/pcProx-demo    
    2019-06-25
"""

import usb.core
import usb.util
from time import sleep
from platform import system


class CardReader():
    def __init__(self):
        # CONFIG
        # Change VENDOR_ID and PRODUCT_ID corresponding to a reader model
        # JRK - changed PROX_END to 4 to accommodate the reader config I use
        # RFID reader config = no stripping of leading or trailing digits.
        self.value = ''
        self.VENDOR_ID = 0x0C27
        self.PRODUCT_ID = 0x3BFA
        self.PROX_END = 4
        self.INTERFACE = 0
        self.CARD_FORMAT = 26
        # END CONFIG
        # Detect the device
        self.dev = usb.core.find(idVendor=self.VENDOR_ID,
                                 idProduct=self.PRODUCT_ID)
        if self.dev is None:
            # raise ValueError('Card reader is not connected')
            self.connected = False
        else:
            # Make sure libusb handles the device
            self.connected = True
            # Ensure OS is not claiming USB interface (not on Win32 though)
            if system() != 'Windows':
                if self.dev.is_kernel_driver_active(self.INTERFACE):
                    print('Detach Kernel Driver')
                    self.dev.detach_kernel_driver(self.INTERFACE)
            # Set a mode
            # ctrl_transfer is used to control endpoint0
            self.dev.set_configuration(1)
            usb.util.claim_interface(self.dev, self.INTERFACE)
            self.dev.ctrl_transfer(0x21, 9, 0x0300, 0, [0x008d])

        self.card_value_initialize()

    def __delete__(self, instance):
        del self.value
        del self.dev
        del self.raw_card_read
        del self.badge_bin

    def read_card(self):
        # Pull the status
        if self.dev is None:
            print('reader disconected')
            self.connected = False
            return False
        else:
            try:
                self.raw_card_read = self.dev.ctrl_transfer(0xA1, 1, 0x0300,
                                                            0, self.PROX_END)
                if self.raw_card_read[0] > 0:
                    self.badge_hex = self.decode_card()
                    '''
                    Get Facility Access Code by slicing the first 8 binary
                    digits & converting to integer. Get Card ID Number by
                    converting the last 16 digits to integer
                    '''
                    self.badge_bin = (bin(int(self.badge_hex, 16)))
                    if self.CARD_FORMAT == 34:
                        self.badge_fac = \
                            self._bin_to_int(self.badge_bin[2:-1][:9])
                    else:
                        self.badge_fac = \
                            self._bin_to_int(self.badge_bin[4:-1][:7])
                    self.badge_num = \
                        self._bin_to_int(self.badge_bin[4:-1][-16:])
                    return True
            except usb.core.USBError:
                self.connected = False
                self.dev = None
                return False

    def wait_for_one_swipe(self):
        last_read = '0x0000'
        while self.dev is not None:
            self.read_card()
            if self.badge_hex != last_read:
                sleep(0.3)
                last_read = self.badge_hex
                print(self.badge_hex)
                print(str(self.badge_num))
                return True

    def swipe_loop(self):
        last_read = '0x0000'
        while 1:
            self.read_card()
            if self.badge_hex != last_read:
                sleep(0.3)
                last_read = self.badge_hex
                print(self.badge_bin)
                print(self.badge_hex)
                print(self.badge_fac)
                print(str(self.badge_num))

    def _bin_to_int(self, binary):
        decimal = 0
        for digit in binary:
            decimal = decimal*2 + int(digit)
        return decimal

    # Convert output into hex
    def decode_card(self):
        proxHex = '0x'
        for h in (reversed(self.raw_card_read)):
            # JRK - added if stmt to handle 1-digit numbers without leading 0
            if (h < 16 and h > 0):
                proxHex += '0' + hex(h)[2:]
            else:
                proxHex += hex(h)[2:]
        # Get 24-digit binary (slice first 2 and last 1 digit from the binary)
        return proxHex

    def decode_card_noreverse(self):
        proxHex = '0x'
        for h in (self.raw_card_read):
            # JRK - added if stmt to handle 1-digit numbers without leading 0
            if (h < 16 and h > 0):
                proxHex += '0' + hex(h)[2:]
            else:
                proxHex += hex(h)[2:]
        # Get 24-digit binary (slice first 2 and last 1 digit from the binary)
        return proxHex

    def card_value_initialize(self):
        self.badge_hex = '0x0000'
        self.badge_fac = 0
        self.badge_num = 0
        self.badge_bin = 0
