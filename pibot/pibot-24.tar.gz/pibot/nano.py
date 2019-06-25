import time

from pibot.serial_comm import write_order, Order, read_i16, read_i8
from pibot.utils import open_serial_port


class Nano:
    def __init__(self):
        try:
            self.serial_file = open_serial_port(baudrate=115200, timeout=None)
        except Exception as e:
            raise e

        is_connected = False

        # Initialize communication with Arduino
        while not is_connected:
            print("Waiting for arduino...")
            write_order(self.serial_file, Order.HELLO)
            bytes_array = bytearray(self.serial_file.read(1))
            if not bytes_array:
                time.sleep(2)
                continue
            byte = bytes_array[0]
            if byte in [Order.HELLO.value, Order.ALREADY_CONNECTED.value]:
                is_connected = True

        print("Connected to Arduino")
        self.serial_file.reset_input_buffer()
        self.serial_file.flush()

    def set_motors(self, left, right):
        pass

    def get_encoders(self):
        pass

    def get_battery_voltage(self):
        write_order(self.serial_file, order=Order.VOLTAGE)
        # self.serial_file.reset_input_buffer()
        # self.serial_file.flush()
        return read_i16(self.serial_file)

    def get_distances(self):
        pass
