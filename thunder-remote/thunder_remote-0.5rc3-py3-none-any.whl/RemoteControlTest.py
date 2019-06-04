from thunder_remote.RemoteControl import RemoteControl

remote = RemoteControl(debug_mode=True)
if remote.is_available():
    # register event handler
    # remote.events.on_north += event_handler

    remote.start()
