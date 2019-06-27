from examples.RemoteControlTest import RemoteControlTest
from thunder_remote.RemoteControl import RemoteControl

if __name__ == "__main__":
    remote = RemoteControl(profile='default', start_sleeping=True, in_proc=False)

    rct = RemoteControlTest(remote)
    if remote.is_available:
        RemoteControl.events.wake_up += rct.wake_up
        RemoteControl.events.on_west += rct.sleep

        RemoteControl.events.on_stick_left_y += rct.print_val
        RemoteControl.events.on_stick_right_y += rct.print_val

        remote.activate()

    while remote.remote_online:
        remote.listen()

        if rct.manualControl:
            remote.active_control()
