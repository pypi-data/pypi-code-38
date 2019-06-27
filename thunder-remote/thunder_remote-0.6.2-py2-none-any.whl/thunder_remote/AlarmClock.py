import threading
from time import sleep

from inputs import get_gamepad
from thunder_remote import ControllerMapping


class AlarmClock:

    def __init__(self):
        pass

    @classmethod
    def wait_for_input(cls):
        """
        The method which is running on start up.

        :return: void
        """
        active = True
        while active:
            events = get_gamepad()

            for _ in events:
                if _.code in ControllerMapping.WAKE_UP:
                    active = False

    @classmethod
    def launch_with_callback(cls, callback):
        def with_callback():
            AlarmClock.wait_for_input()
            callback()

        clock = threading.Thread(target=with_callback)
        clock.start()
        sleep(5)
        return clock
