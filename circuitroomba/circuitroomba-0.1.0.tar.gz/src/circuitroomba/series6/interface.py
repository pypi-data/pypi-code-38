import time
import busio
import digitalio
from .opcode import commands, mode_commands, valid_modes


class OpenInterface:
    """
    This class maps the pins on your board (where Circuit Python is executing) to the
    Roomba Open Interface.

    This class is focused on lower level details of the Open Interface spec while the
    Roomba class exposes higher level help methods and operations.


          6
    7 - . . . - 5
    4 - .   . - 3
     2 - . . - 1


    Pin 1 - Vpwr - Roomba Battery + (unregulated)
    Pin 2 - Vpwr - Roomba Battery + (unregulated)
    Pin 3 - RXD - 0-5V Serial Input to Roomba
    Pin 4 - TXD - 0-5V Serial Output from Rooba
    Pin 5 - BRC - Baud rate change
    Pin 6 - GND - Roomba battery ground
    Pin 7 - GND - Roomba battery ground

    Serial Port Settings
    Baud: 115200 or 19200 (see below) Data bits: 8
    Parity: None
    Stop bits: 1
    Flow control: None

    By default, Roomba communicates at 115200 baud. If you are using a microcontroller
    that does not support 115200 baud, there are two ways to force Roomba to switch to
    19200:

    https://www.irobotweb.com/~/media/MainSite/PDFs/About/STEM/Create/iRobot_Roomba_600_Open_Interface_Spec.pdf # noqa
    """

    def __init__(self, tx_pin, rx_pin, brc_pin, baud_rate=115200, trace=False):
        """
        Initialize communication pins and state. State is referred to as
        operating mode to stay consistent with the Open Interface Specification
        document.

        Two list are created to capture operating mode and command history. Both
        store the last 5 items processed.

        If trace is enabled the last 10 commands will be captured in self.history.

        History tuple structure:
        (operating_mode, command, data_bytes)
        """
        self._board = busio.UART(tx_pin, rx_pin, baudrate=baud_rate)
        self._tx_pin = tx_pin
        self._rx_pin = rx_pin
        self._brc_pin = brc_pin
        self._baud_rate = baud_rate
        self._operating_mode = "off"
        self.trace = trace

        # Could be expensive for an embedded environment.
        if trace:
            self._history = [None for i in range(10)]

        self._brc_pin.direction = digitalio.Direction.OUTPUT

    @property
    def valid_modes(self):
        return valid_modes

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, new_history):
        for i in range(1, len(self._history)):
            self._history[-i] = self._history[-(i + 1)]
        self._history[0] = new_history

    @property
    def operating_mode(self):
        return self._operating_mode

    @operating_mode.setter
    def operating_mode(self, new_mode):
        """
        Track the current operating mode of the Roomba to verify that the next
        command is valid in the current mode. The mode is not written to the
        board or transmitted to the Roomba because the Roomba has an internal
        state that is maintained and changed based on the sequence of commands.
        """
        if new_mode and new_mode in valid_modes:
            self._operating_mode = new_mode
        # instead of just using an else need to do an elif since new_mode can be None
        # for a noop operating mode change
        elif new_mode and new_mode not in valid_modes:
            raise RuntimeError(
                "New mode %s is not a valid mode.\n"
                "See page 5 of the open interface specification or refer to the"
                " OpenInterface valid_modes attribute." % (new_mode)
            )

    def command(self, new_command, data=0):
        """
        Accepts an inbound command that should be sent to the OI RX pin.
        Data should be an int inline with the OI specification document
        that will be handled as bytes internally.

        Command is called to handle validation of the mode and state
        transition as well as verify the data matches spec requirements.
        """
        command_struct = commands[new_command]
        bdata = bytes([data])

        if new_command in mode_commands[self.operating_mode]:
            self._board.write(new_command)
        else:
            raise RuntimeError(
                "Illegal command in current mode.\n"
                "Cannot call %s in %s mode.\n"
                "Refer to the Roomba 600 Interface Spec for more information.\n"
                % (new_command, self.operating_mode)
            )

        if data and len(bdata) == command_struct["data_bytes"]:
            print(bdata)
            self._board.write(bdata)
        elif data and len(bdata) != command_struct["data_bytes"]:
            raise RuntimeError(
                "Correct amount of data bytes not provided for command.\n"
                "Expected %s \n"
                "Recieved %s.\n"
                "Refer to command %s in Roomba Open Interface Spec for data byte "
                "information" % (command_struct["data_bytes"], len(bdata), new_command)
            )

        self.operating_mode = command_struct["new_mode"]

        if self.trace:
            self.history = (command_struct["new_mode"], new_command, bdata)

    @property
    def baud_rate(self):
        return self._baud_rate

    @baud_rate.setter
    def baud_rate(self, rate):
        self._baud_rate = rate

    def _brc_set_baud_rate(self, baud_rate=19200):
        """
        Function should be the first call after the circuitroomba is powered on
        to set new BRC. This is not required if your boards baud rate is
        115200.

        For manipulating baud rate after commands have been issued
        use the baud command from the Open Interface spec.

        See page 4 of the Open Interface Create 2/Series 6 manual for
        information on setting the baud rate at startup.
        """

        for i in range(3):
            self._brc_pin.value = False
            time.sleep(0.25)
            self._brc_pin.value = True
            time.sleep(0.25)

        self.baud_rate = baud_rate

    def wake_up(self):
        """
        If the circuitroomba is in passive mode without any byte activity on the RX pin
        for 5 minutes it will will enter into a sleep mode. To wake it up
        you need to pulse the RX pin LOW/HIGH/LOW.
        """

        for i in range(3):
            self._brc_pin.value = False
            time.sleep(0.5)
            self._brc_pin.value = True
            time.sleep(0.5)
            self._brc_pin.value = False
            time.sleep(0.5)

    def keep_awake(self, duty_cycle=60):
        """
        In passive mode the circuitroomba will go into a sleep mode after 5 minutes
        without activity. To prevent this we can pulse the BRC pin low on
        a given duty_cycle.

        Currently need a way to put this into a queue, a background thread,
        async task etc that sleeps for the duty cycle wakes up to pulse the
        brc pin and then goes into the background again.
        """
        raise NotImplementedError
