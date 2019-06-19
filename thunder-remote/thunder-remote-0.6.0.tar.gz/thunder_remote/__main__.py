import argparse

from thunder_remote.DebugLevel import DebugLevel
from thunder_remote.RemoteControl import RemoteControl


mc = True


def wake_up(rc):
    global mc
    print "> WAKE UP"

    rc.wake()
    mc = True


def sleep(rc):
    global mc
    print "> SLEEP"

    rc.sleep()
    mc = False


def kill_rc(rc):
    rc.deactivate()


def any(code, state):
    print "> [DEBUG] ANY EVENT: {0} : {1}".format(code, state)


def print_val(state):
    print "> {0}".format(state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Init Thunder-Remote')
    parser.add_argument('-p', '--profile', metavar='name', default="default", help='the controller profile to load')
    parser.add_argument('-s', '--sleeping', default=not mc, help='start the controller sleeping')

    args = parser.parse_args()

    remote = RemoteControl(profile=args.profile, start_sleeping=args.sleeping, debug_level=DebugLevel.NONE, in_proc=False)
    if remote.is_available:
        RemoteControl.events.wake_up += lambda: wake_up(remote)
        RemoteControl.events.on_west += lambda code, state: sleep(remote)
        RemoteControl.events.on_any += lambda code, state: any(code, state)
        RemoteControl.events.on_select += lambda code, state: kill_rc(remote)

        RemoteControl.events.on_stick_left_y += lambda code, state: print_val(state)
        RemoteControl.events.on_stick_right_y += lambda code, state: print_val(state)

        remote.activate()

    while True:
        remote.listen()

        if mc:
            remote.active_control()

        if remote.is_available:
            pass
