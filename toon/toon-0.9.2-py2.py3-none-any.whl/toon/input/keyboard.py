from toon.input.base_input import BaseInput
from pynput import keyboard
from ctypes import c_bool, c_uint16, c_char


class Keyboard(BaseInput):
    """Keyboard interface."""

    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 100)

    @staticmethod
    def data_shapes(**kwargs):
        return [[1], [1], [1]]

    @staticmethod
    def data_types(**kwargs):
        return [c_bool, c_uint16, c_char]

    def __init__(self, keys=None, **kwargs):
        """
        Args:
            keys (list): Keys of interest, e.g. `['a', 's', 'd', 'f']`
            **kwargs: Keyword arguments passed to `toon.input.base_input.BaseInput`.
        """
        self.keys = keys
        super(Keyboard, self).__init__(**kwargs)

    def __enter__(self):
        self._on = []
        self.pressed = []
        self.index = []
        self.char = []
        self.times = []
        self.dev = keyboard.Listener(on_press=self.on_press,
                                     on_release=self.on_release)
        self.dev.start()
        self.dev.wait()
        return self

    def __exit__(self, *args):
        self.dev.stop()
        self.dev.join()

    def read(self):
        """Returns all key press/release events since the last `read()` call.

        The first data element is boolean (whether key event was press or release),
        the second element is the position of the key in the `keys` list provided at instantiation,
        and the third element is the character representation of the key."""
        if not self.times:
            return None, None
        time2 = []
        pressed2 = []
        index2 = []
        char2 = []
        time2[:] = self.times
        pressed2[:] = self.pressed
        index2[:] = self.index
        char2[:] = self.char
        self.times = []
        self.pressed = []
        self.index = []
        self.char = []
        return time2[-1], [pressed2[-1], index2[-1], char2[-1]]

    def on_press(self, key):
        ts = self.clock()
        if not isinstance(key, keyboard.Key):
            if key.char in self.keys and key.char not in self._on:
                index = self.keys.index(key.char)
                self.pressed.append(True)
                self.index.append(index)
                self.char.append(key.char)
                self.times.append(ts)
                self._on.append(key.char)

    def on_release(self, key):
        ts = self.clock()
        if not isinstance(key, keyboard.Key):
            if key.char in self.keys and key.char in self._on:
                index = self.keys.index(key.char)
                self.pressed.append(False)
                self.index.append(index)
                self.char.append(key.char)
                self.times.append(ts)
                self._on.remove(key.char)
