import os
import os.path
from collections import deque

RECORDS_CAPTURED = deque()
KINESIS_FOLDER = os.path.join(os.path.expanduser("~"), ".kinesis")
CAPTURES_FOLDER = os.path.join(os.path.expanduser("~"), ".kinesis/captures")


def create_config_dir():
    """Creates a folder named .kinesis in user's home directory"""
    if not os.path.isdir(KINESIS_FOLDER):
        os.mkdir(KINESIS_FOLDER)
    if not os.path.isdir(CAPTURES_FOLDER):
        os.mkdir(CAPTURES_FOLDER)


def init():
    create_config_dir()
    global RECORDS_CAPTURED  # pylint: disable=global-statement
