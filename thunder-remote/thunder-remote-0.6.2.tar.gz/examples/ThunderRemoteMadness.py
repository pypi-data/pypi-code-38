from examples.RemoteControlTest import RemoteControlTest
from thunder_remote.RemoteControl import RemoteControl

if __name__ == "__main__":
    remote = RemoteControl(profile='madness', start_sleeping=False, in_proc=False)

    rct = RemoteControlTest(remote)
    if remote.is_available:
        RemoteControl.events.on_west += rct.on_west
        RemoteControl.events.on_north += rct.on_north
        RemoteControl.events.on_east += rct.on_east
        RemoteControl.events.on_south += rct.on_south

        remote.activate()

    while remote.remote_online:
        remote.listen()

        if rct.manualControl:
            remote.active_control()
