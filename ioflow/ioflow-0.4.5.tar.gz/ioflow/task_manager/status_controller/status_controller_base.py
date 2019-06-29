class StatusControllerBase(object):
    PAUSE = 'pause'
    CONTINUE = 'continue'
    STOP = 'stop'

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, pause_event, stop_event):
        return self.main(pause_event, stop_event)

    def main(self, pause_event, stop_event):
        return NotImplementedError

    def exec(self, cmd, pause_event, stop_event):
        if cmd not in [self.PAUSE, self.CONTINUE, self.STOP]:
            raise ValueError()

        if cmd == self.STOP:
            stop_event.set()

        if cmd == self.PAUSE:
            if not pause_event.is_set():
                return "Already pause"
            else:
                pause_event.clear()

        elif cmd == self.CONTINUE:
            if pause_event.is_set():
                return "Process is not paused"
            else:
                pause_event.set()
