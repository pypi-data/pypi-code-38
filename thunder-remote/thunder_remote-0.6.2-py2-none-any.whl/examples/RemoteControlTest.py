from __future__ import print_function


class RemoteControlTest:
    def __init__(self, remote_control):
        """

        :param remote_control:
        """

        self.manualControl = True
        self.rc = remote_control

    def wake_up(self):
        """

        """

        print("> WAKE UP")

        self.rc.wake()
        self.manualControl = True

    def sleep(self, *_):
        """

        """

        print("> SLEEP")

        self.rc.sleep()
        self.manualControl = False

    @staticmethod
    def on_north(*_):
        print('on_north event fired')

    @staticmethod
    def on_east(*_):
        print('on_east event fired')

    @staticmethod
    def on_south(*_):
        print('on_east event fired')

    @staticmethod
    def on_west(*_):
        print('on_east event fired')

    @staticmethod
    def any(code, state):
        print("> {0} -> {1}".format(code, state))

    @staticmethod
    def print_val(_, state):
        """

        :param _:
        :param state:
        """

        print("> {0}".format(state))
