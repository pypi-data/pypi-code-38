from kivy import graphics
from kivy.uix.label import Label
import threading
import time

STATES = 'normal', 'down'


class Bang(Label):
    def __init__(self, text, delay=0.25, **kwds):
        super().__init__(text=text, **kwds)
        self.delay = delay
        self.lock = threading.RLock()
        self._state = False

    @property
    def _state(self):
        return self.state == STATES[1]

    @_state.setter
    def _state(self, state):
        self.state = STATES[bool(state)]
        self.on_size()

    def bang(self):
        with self.lock:
            self.target_time = time.time() + self.delay
            if not self._state:
                self._state = True
                threading.Thread(target=self._target, daemon=True).start()

    def on_size(self, *args):
        self.canvas.clear()
        if self._state:
            with self.canvas:
                graphics.Color(0, 1, 1)
                graphics.Rectangle(pos=self.pos, size=self.size)

    def _target(self):
        while True:
            with self.lock:
                remains = self.target_time - time.time()
                if remains <= 0:
                    self._state = False
                    break
            time.sleep(remains)
