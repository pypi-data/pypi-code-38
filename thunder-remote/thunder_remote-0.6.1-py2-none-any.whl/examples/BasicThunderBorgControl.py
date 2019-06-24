from __future__ import print_function

import argparse
from thunder_remote.DebugLevel import DebugLevel
from thunder_remote.RemoteControl import RemoteControl


class RemoteControlTest:
    def __init__(self, remote_control):
        self.manualControl = True
        self.rc = remote_control

    def wake_up(self):
        print("> WAKE UP")

        self.rc.wake()
        self.manualControl = True

    def sleep(self):
        print("> SLEEP")

        self.rc.sleep()
        self.manualControl = False

    def kill_rc(self):
        self.rc.deactivate()
        self.manualControl = False

    @staticmethod
    def any(code, state):
        print("> [DEBUG] ANY EVENT: {0} : {1}".format(code, state))

    @staticmethod
    def print_val(state):
        print("> {0}".format(state))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Init Thunder-Remote')
    parser.add_argument('-p', '--profile', metavar='name', default="default", help='the controller profile to load')
    args = parser.parse_args()

    remote = RemoteControl(profile=args.profile, start_sleeping=True, debug_level=DebugLevel.NONE,
                           in_proc=False)

    rct = RemoteControlTest(remote)
    if remote.is_available:
        RemoteControl.events.wake_up += lambda: rct.wake_up()
        RemoteControl.events.on_west += lambda code, state: rct.sleep()
        RemoteControl.events.on_any += lambda code, state: rct.any(code, state)
        RemoteControl.events.on_select += lambda code, state: rct.kill_rc()

        RemoteControl.events.on_stick_left_y += lambda code, state: rct.print_val(state)
        RemoteControl.events.on_stick_right_y += lambda code, state: rct.print_val(state)

        remote.activate()

    while remote.remote_online:
        remote.listen()

        if rct.manualControl:
            remote.active_control()
