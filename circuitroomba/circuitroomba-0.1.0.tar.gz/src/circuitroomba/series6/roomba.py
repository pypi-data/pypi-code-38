import time
from .opcode import (
    START,
    STOP,
    RESET,
    BAUD,
    SAFE,
    FULL,
    CLEAN,
    MAX_CLEAN,
    SPOT,
    FORCE_SEEKING_DOCK,
    POWER,
    baud_codes,
)
from .interface import OpenInterface


class Commands(OpenInterface):
    """
    Commands is an abstraction layer that exposes methods representing the operations
    available in the Roomba Open Interface Spec.

    >>> bot = roomba.Commands(board.TX, board.RX, board.A1)
    >>> bot.wake_up()
    >>> bot.start()
    >>> bot.clean()
    """

    def __init__(self, tx_pin, rx_pin, brc_pin, baud_rate=115200, trace=False):
        super().__init__(tx_pin, rx_pin, brc_pin, baud_rate, trace)

    def __repr__(self):
        return (
            "Roomba pin mapping\nRX PIN: %s\nTX PIN %s\nBAUD RATE CHANGE PIN %s\n",
            self._rx_pin,
            self._tx_pin,
            self._brc_pin,
        )

    def set_baud_rate_19200(self):
        """
        By default the Roomba Open Interface listens for commands at baud rate 115200.
        If you have a controller that needs to use 19200 on serial instead this method
        should be called right after the Roomba wakes up before any other commands.
        """
        self._brc_set_baud_rate()

    def start(self):
        """
        This command starts the OI.

        You must always send the Start command before sending any other commands
        to the OI.

        - Serial sequence: [128].
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: Passive. Roomba beeps once to acknowledge it is starting
          from “off” mode.
        """

        self.command(START)

    def reset(self):
        """
        This command resets the robot, as if you had removed and reinserted the battery.

        - Serial sequence: [7].
        - Available in modes: Always available.
        - Changes mode to: Off. You will have to send start again to re-enter Open
          Interface mode.
        """

        self.command(RESET)

    def stop(self):
        """
        This command stops the OI. All streams will stop and the robot will no
        longer respond to commands. Use this command when you are finished working
        with the robot.

        - Serial sequence: [173].
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: Off. Roomba plays a song to acknowledge it is exiting the OI.
        """
        self.command(STOP)

    def baud(self, baud_rate_code=None):
        """
        This command sets the baud rate in bits per second (bps) at which OI commands
        and data are sent according to the baud code sent in the data byte. The default
        baud rate at power up is 115200 bps, but the starting baud rate can be changed
        to 19200 by following the method outlined on page 4. Once the baud rate is
        changed, it persists until Roomba is power cycled by pressing the power button
        or removing the battery, or when the battery voltage falls below the minimum
        required for processor operation. You must wait 100ms after sending this command
        before sending additional commands at the new baud rate.

        - Serial sequence: [129][Baud Code]
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: No Change
        - Baud data byte 1: Baud Code (0 - 11)
        """

        if baud_rate_code in baud_codes.keys():
            self.baud_rate = baud_codes[baud_rate_code]
            self.command(BAUD, baud_rate_code)
            # per the OI spec another command cannot be issued after the baud command
            # for 100ms
            time.sleep(1 / 1000000)
        else:
            raise RuntimeError(
                "Invalid baud rate code. Please refer to page 9 of the"
                "Roomba Open Interface Spec."
            )

    def safe(self):
        """
        Safe Opcode: 131 Data Bytes: 0
        This command puts the OI into Safe mode, enabling user control of Roomba.
        It turns off all LEDs. The OI can be in Passive, Safe, or Full mode to accept
        this command. If a safety condition occurs (see above) Roomba reverts
        automatically to Passive mode.

        - Serial sequence: [131]
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: Safe

        Note: The effect and usage of the Control command (130) are identical to the
        Safe command (131).
        """
        self.command(SAFE)

    def full(self):
        """
        This command gives you complete control over Roomba by putting the OI into
        Full mode, and turning off the cliff, wheel-drop and internal charger safety
        features. That is, in Full mode, Roomba executes any command that you send it,
        even if the internal charger is plugged in, or command triggers a cliff or
        wheel drop condition.

        - Serial sequence: [132]
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: Full

        Note: Use the Start command (128) to change the mode to Passive.
        """
        self.command(FULL)

    def clean(self):
        """
        This command starts the default cleaning mode. This is the same as pressing
        Roomba’s Clean button, and will pause a cleaning cycle if one is already in
        progress.

        - Serial sequence: [135]
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: Passive
        """
        self.command(CLEAN)

    def max(self):
        """
        This command starts the Max cleaning mode, which will clean until the battery
        is dead. This command will pause a cleaning cycle if one is already in progress.

        - Serial sequence: [136]
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: Passive
        """
        self.command(MAX_CLEAN)

    def spot(self):
        """
        This command starts the Spot cleaning mode. This is the same as pressing
        Roomba’s Spot button, and will pause a cleaning cycle if one is already in
        progress.

        - Serial sequence: [134]
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: Passive
        """
        self.command(SPOT)

    def seek_dock(self):
        """
        This command directs Roomba to drive onto the dock the next time it encounters
        the docking beams. This is the same as pressing Roomba’s Dock button, and will
        pause a cleaning cycle if one is already in progress.

        - Serial sequence: [143]
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: Passive
        """
        self.command(FORCE_SEEKING_DOCK)

    def power(self):
        """
        This command powers down Roomba. The OI can be in Passive, Safe, or Full mode
        to accept this command.

        - Serial sequence: [133]
        - Available in modes: Passive, Safe, or Full
        - Changes mode to: Passive
        """
        self.command(POWER)
