from serial import Serial


class Xtend(Serial):
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        super(Xtend, self).__init__(port=port, baudrate=baudrate)

    def testing(self):
        self.write("testing\n")
