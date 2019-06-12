import unittest
from circuitroomba.series6 import opcode


class Test_opcode_are_set_correct(unittest.TestCase):
    """
    Validating hex codes set in opcode translate to the correct byte codes
    found on page 33 of the Roomba Open Interface Spec
    """

    def test_start(self):
        self.assertEqual(opcode.START, bytes([128]))

    def test_baud_rate(self):
        self.assertEqual(opcode.BAUD, bytes([129]))

    def test_control(self):
        self.assertEqual(opcode.CONTROL, bytes([130]))

    def test_safe(self):
        self.assertEqual(opcode.SAFE, bytes([131]))

    def test_full(self):
        self.assertEqual(opcode.FULL, bytes([132]))

    def test_power(self):
        self.assertEqual(opcode.POWER, bytes([133]))

    def test_spot(self):
        self.assertEqual(opcode.SPOT, bytes([134]))

    def test_clean(self):
        self.assertEqual(opcode.CLEAN, bytes([135]))

    def test_max_clean(self):
        self.assertEqual(opcode.MAX_CLEAN, bytes([136]))

    def test_drive(self):
        self.assertEqual(opcode.DRIVE, bytes([137]))

    def test_motors(self):
        self.assertEqual(opcode.MOTORS, bytes([138]))

    def test_pwm_moros(self):
        self.assertEqual(opcode.PWM_MOTORS, bytes([144]))

    def test_drive_pwm(self):
        self.assertEqual(opcode.DRIVE_PWM, bytes([146]))

    def test_leds(self):
        self.assertEqual(opcode.LEDS, bytes([139]))

    def test_song(self):
        self.assertEqual(opcode.SONG, bytes([140]))

    def test_play(self):
        self.assertEqual(opcode.PLAY, bytes([141]))

    def test_stream(self):
        self.assertEqual(opcode.STREAM, bytes([148]))

    def test_query_list(self):
        self.assertEqual(opcode.QUERY_LIST, bytes([149]))

    def test_do_stream(self):
        self.assertEqual(opcode.DO_STREAM, bytes([150]))

    def test_query(self):
        self.assertEqual(opcode.QUERY, bytes([142]))

    def test_force_seeking_doc(self):
        self.assertEqual(opcode.FORCE_SEEKING_DOCK, bytes([143]))

    def test_scheduling_leds(self):
        self.assertEqual(opcode.SCHEDULING_LEDS, bytes([162]))

    def test_digit_leds_raw(self):
        self.assertEqual(opcode.DIGIT_LEDS_RAW, bytes([163]))

    def test_digit_leds_ascii(self):
        self.assertEqual(opcode.DIGIT_LEDS_ASCII, bytes([164]))

    def test_buttons(self):
        self.assertEqual(opcode.BUTTONS, bytes([165]))

    def test_schedule(self):
        self.assertEqual(opcode.SCHEDULE, bytes([167]))

    def test_set_day_time(self):
        self.assertEqual(opcode.SET_DAY_TIME, bytes([168]))

    def test_stop(self):
        self.assertEqual(opcode.STOP, bytes([173]))
