import time

from pibot.serial_comm import write_order, Order, read_i16, write_i8, read_ui8
from pibot.utils import open_serial_port, clamp

import struct


class Nano:
    def __init__(self):
        try:
            self.serial_file = open_serial_port(baudrate=115200, timeout=None)
        except Exception as e:
            raise e

        is_connected = False

        # Initialize communication with Arduino
        print("Requesting Connection to Nano...")
        while not is_connected:
            write_order(self.serial_file, Order.START)
            if self.serial_file.inWaiting():
                byte = self.serial_file.read(1)
                if struct.unpack('B', byte)[0] == Order.CONNECTED.value:
                    is_connected = True
            else:
                time.sleep(1)
        print("Connected to Nano.")

    def set_stat_led(self, toggle):
        write_order(self.serial_file, order=Order.STAT_LED)
        write_i8(self.serial_file, toggle)

    def set_motors(self, left, right):
        write_order(self.serial_file, order=Order.MOTORS)
        # Write left
        write_i8(self.serial_file, clamp(left, -128, 127))
        # Write right
        write_i8(self.serial_file, clamp(right, -128, 127))

    def get_encoders(self):
        write_order(self.serial_file, order=Order.GET_ENCODERS)
        # Wait for 2 values
        left = read_i16(self.serial_file)
        right = read_i16(self.serial_file)
        return left, right

    def reset_encoders(self):
        write_order(self.serial_file, order=Order.RESET_ENCODERS)

    def get_battery_voltage(self):
        write_order(self.serial_file, order=Order.VOLTAGE)
        return read_i16(self.serial_file)

    def get_distances(self):
        write_order(self.serial_file, order=Order.DISTANCES)
        # Wait for 3 values
        left = read_ui8(self.serial_file)
        mid = read_ui8(self.serial_file)
        right = read_ui8(self.serial_file)
        return left, mid, right
