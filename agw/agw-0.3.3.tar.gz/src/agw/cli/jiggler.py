import itertools
from agw import Automater
from .util import ctrl_exit


def move_cursor(cursor, movement):
    def _move_cursor():
        x, y = cursor.position
        return x + movement

    return _move_cursor


@ctrl_exit
def jiggle():
    auto = Automater()
    cursor = auto.cursor

    cycle = itertools.cycle((move_cursor(cursor, 5), move_cursor(cursor, -5)))

    while True:
        x, y = cursor.position
        cursor.to(next(cycle)(), y)
        auto.pause(5)
