import sys
from time import sleep
from agw import Cursor
from .util import ctrl_exit


@ctrl_exit
def position():
    cursor = Cursor()
    last_position = (-1, -1)
    while True:
        current_position = cursor.position
        if current_position == last_position:
            sys.stdout.write("*")
            sys.stdout.flush()
        else:
            last_position = current_position
            x, y = current_position
            sys.stdout.write("\n")
            sys.stdout.write(f"x: {x: >4}  y: {y: >4} ")
            sys.stdout.flush()
        sleep(1)
