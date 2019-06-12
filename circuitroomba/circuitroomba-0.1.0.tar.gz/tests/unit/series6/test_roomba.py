import unittest
import time
from unittest import mock
from circuitroomba.series6 import roomba


class Test_roomba_commands(unittest.TestCase):
    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_roomba_roomba_fails_to_send_new_command_to_fast_after_baud_change(
        self, uart, busio
    ):
        with self.assertRaises(RuntimeError):
            board = mock.MagicMock()
            bot = roomba.Commands(board.RX, board.TX, board.A1)
            bot.wake_up()
            bot.baud(8)
            bot.start()

    @mock.patch("circuitroomba.series6.interface.busio", return_value=mock.MagicMock())
    @mock.patch(
        "circuitroomba.series6.interface.busio.UART", return_value=mock.MagicMock()
    )
    def test_roomba_roomba_sends_new_command_after_baud_change_with_wait(
        self, uart, busio
    ):
        board = mock.MagicMock()
        bot = roomba.Commands(board.RX, board.TX, board.A1)
        bot.wake_up()
        bot.start()
        bot.baud(3)
        time.sleep(0.5)
        bot.stop()
        self.assertEqual(bot.baud_rate, 2400)
