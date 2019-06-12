import unittest
from unittest import mock
from circuitroomba.series6 import interface, opcode


class Test_interface(unittest.TestCase):
    """
    interface is initialized in each test to prevent carrying over
    any state or history from test to test.
    """

    def setUp(self) -> None:
        self.board = mock.MagicMock()

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_history_not_available_by_default(self, uart, busio):
        oi = interface.OpenInterface(self.board.RX, self.board.TX, self.board.A1)
        self.assertEqual(False, oi.trace)
        self.assertEqual(False, hasattr(oi, "history"))

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_valid_modes_return_only_valid_modes(self, uart, busio):
        oi = interface.OpenInterface(
            self.board.RX, self.board.TX, self.board.A1, trace=True
        )

        self.assertEqual(oi.valid_modes, ("off", "safe", "passive", "full"))

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_change_operating_mode(self, uart, busio):
        oi = interface.OpenInterface(
            self.board.RX, self.board.TX, self.board.A1, trace=True
        )

        oi.operating_mode = "safe"
        self.assertEqual(oi.operating_mode, "safe")

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_invalid_operating_mode(self, uart, busio):
        oi = interface.OpenInterface(
            self.board.RX, self.board.TX, self.board.A1, trace=True
        )

        with self.assertRaises(RuntimeError):
            oi.operating_mode = "kernel"

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_send_new_command(self, uart, busio):
        oi = interface.OpenInterface(
            self.board.RX, self.board.TX, self.board.A1, trace=True
        )

        oi.command(opcode.START)
        self.assertEqual(oi.history[0][1], opcode.START)

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_history_cannot_exceed_10(self, uart, busio):
        oi = interface.OpenInterface(
            self.board.RX, self.board.TX, self.board.A1, trace=True
        )

        for i in range(15):
            oi.command(opcode.START)

        self.assertEqual(len(oi.history), 10)

        for i in range(9):
            self.assertEqual(oi.history[i], ("passive", opcode.START, b"\x00"))

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_send_invalid_command(self, uart, busio):
        oi = interface.OpenInterface(
            self.board.RX, self.board.TX, self.board.A1, trace=True
        )

        with self.assertRaises(KeyError):
            oi.command("0x10")

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_send_invalid_command_for_current_operating_mode(self, uart, busio):
        oi = interface.OpenInterface(
            self.board.RX, self.board.TX, self.board.A1, trace=True
        )

        with self.assertRaises(RuntimeError):
            oi.command(opcode.STOP)
            oi.command(opcode.BAUD, 11)

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_send_new_command_with_data(self, uart, busio):
        oi = interface.OpenInterface(
            self.board.RX, self.board.TX, self.board.A1, trace=True
        )
        oi.wake_up()
        oi.command(opcode.START)
        oi.command(opcode.BAUD, 11)
        self.assertEqual(oi.history[1], ("passive", opcode.START, b"\x00"))
        self.assertEqual(oi.history[0], (None, opcode.BAUD, b"\x0b"))

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_send_new_command_with_invalid_data(self, uart, busio):
        oi = interface.OpenInterface(
            self.board.RX, self.board.TX, self.board.A1, trace=True
        )

        with self.assertRaises(RuntimeError):
            oi.command(opcode.RESET, 11)

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_keep_awake_is_not_available(self, uart, busio):
        oi = interface.OpenInterface(self.board.RX, self.board.TX, self.board.A1)

        with self.assertRaises(NotImplementedError):
            oi.keep_awake()
