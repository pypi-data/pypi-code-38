from examples.RemoteControlTest import RemoteControlTest
from thunder_remote.DebugLevel import DebugLevel
from thunder_remote.RemoteControl import RemoteControl

if __name__ == "__main__":
    remote = RemoteControl(profile='default', start_sleeping=False, in_proc=False, debug_level=DebugLevel.EVENT)

    rct = RemoteControlTest(remote)
    if remote.is_available:
        RemoteControl.events.on_any += rct.any

        remote.activate()

    while remote.remote_online:
        remote.listen()

        if rct.manualControl:
            remote.active_control()
