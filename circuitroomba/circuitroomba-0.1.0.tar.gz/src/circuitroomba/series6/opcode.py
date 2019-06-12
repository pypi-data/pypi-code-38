# circuitroomba opcodes
# https://www.irobotweb.com/-/media/MainSite/PDFs/About/STEM/Create/iRobot_Roomba_600_Open_Interface_Spec.pdf?la=en

START = b"\x80"
RESET = b"\x07"
BAUD = b"\x81"
CONTROL = b"\x82"
SAFE = b"\x83"
FULL = b"\x84"
POWER = b"\x85"
SPOT = b"\x86"
CLEAN = b"\x87"
MAX_CLEAN = b"\x88"
DRIVE = b"\x89"
MOTORS = b"\x8A"
PWM_MOTORS = b"\x90"
DRIVE_PWM = b"\x92"
LEDS = b"\x8B"
SONG = b"\x8C"
PLAY = b"\x8D"
STREAM = b"\x94"
QUERY_LIST = b"\x95"
DO_STREAM = b"\x96"
QUERY = b"\x8E"
FORCE_SEEKING_DOCK = b"\x8F"
SCHEDULING_LEDS = b"\xA2"
DIGIT_LEDS_RAW = b"\xA3"
DIGIT_LEDS_ASCII = b"\xA4"
BUTTONS = b"\xA5"
SCHEDULE = b"\xA7"
SET_DAY_TIME = b"\xA8"
STOP = b"\xAD"
SAFE = b"\x83"
FULL = b"\x84"


baud_codes = {
    0: 300,
    1: 600,
    2: 1200,
    3: 2400,
    4: 4800,
    5: 9600,
    6: 14400,
    7: 19200,
    8: 28800,
    9: 38400,
    10: 57600,
    11: 115200,
}

valid_modes = ("off", "safe", "passive", "full")

# Only SAFE and FULL have opcodes in the OI spec, because of that mode names
# are used for keys instead of hex codes differing from commands.
mode_commands = {
    "passive": (
        START,
        RESET,
        STOP,
        BAUD,
        SAFE,
        FULL,
        CLEAN,
        MAX_CLEAN,
        SPOT,
        FORCE_SEEKING_DOCK,
        POWER,
    ),
    "safe": (
        START,
        RESET,
        STOP,
        BAUD,
        SAFE,
        FULL,
        CLEAN,
        MAX_CLEAN,
        SPOT,
        FORCE_SEEKING_DOCK,
        POWER,
    ),
    "full": (
        START,
        RESET,
        STOP,
        BAUD,
        SAFE,
        FULL,
        CLEAN,
        MAX_CLEAN,
        SPOT,
        FORCE_SEEKING_DOCK,
        POWER,
    ),
    "off": (START, RESET),
}

commands = {
    START: {"int_opcode": 128, "data_bytes": 0, "new_mode": "passive"},
    RESET: {"int_opcode": 7, "data_bytes": 0, "new_mode": "off"},
    STOP: {"int_opcode": 173, "data_bytes": 0, "new_mode": "off"},
    BAUD: {"int_opcode": 129, "data_bytes": 1, "new_mode": None},  # new mode noop
    SAFE: {"int_opcode": 131, "data_bytes": 0, "new_mode": "safe"},
    FULL: {"int_opcode": 132, "data_bytes": 0, "new_mode": "full"},
    CLEAN: {"int_opcode": 135, "data_bytes": 0, "new_mode": "passive"},
    MAX_CLEAN: {"int_opcode": 136, "data_bytes": 0, "new_mode": "passive"},
    SPOT: {"int_opcode": 134, "data_bytes": 0, "new_mode": "passive"},
    FORCE_SEEKING_DOCK: {"int_opcode": 143, "data_bytes": 0, "new_mode": "passive"},
    POWER: {"int_opcode": 133, "data_bytes": 0, "new_mode": "passive"},
}
