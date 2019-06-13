import argparse

from thunder_remote.DebugLevel import DebugLevel
from thunder_remote.RemoteControl import RemoteControl


def wake_up(rc):
    print "> WAKE UP"

    rc.wake()


def sleep(rc):
    print "> SLEEP"

    rc.sleep()


def kill_rc(rc):
    rc.deactivate()


def any(code, state):
    print "> [DEBUG] ANY EVENT: {0} : {1}".format(code, state)


def print_val(state):
    print "> {0}".format(state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Init Thunder-Remote')
    parser.add_argument('-p', '--profile', metavar='name', default="default", help='the controller profile to load')
    parser.add_argument('-s', '--sleeping', default=True, help='start the controller sleeping')

    args = parser.parse_args()

    remote = RemoteControl(profile=args.profile, start_sleeping=args.sleeping, debug_level=DebugLevel.NONE)
    if remote.is_available:
        remote.events.wake_up += lambda: wake_up(remote)
        remote.events.on_west += lambda code, state: sleep(remote)
        remote.events.on_any += lambda code, state: any(code, state)
        remote.events.on_select += lambda code, state: kill_rc(remote)

        remote.events.on_stick_left_y += lambda code, state: print_val(state)
        remote.events.on_stick_right_y += lambda code, state: print_val(state)

        remote.activate()

    while remote.remote_online:
        remote.listen()
        if remote.is_available:
            pass
