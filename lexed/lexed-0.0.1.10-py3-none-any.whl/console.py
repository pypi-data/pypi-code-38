import threading


class Curses:
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = super().__new__(cls)
        return cls.__singleton_instance

    def __init__(self):
        temp = __import__('curses')
        self._screen = temp.initscr()
        for key in temp.__dict__:
            if key != 'initscr' and not key.startswith('_'):
                setattr(self, key, getattr(temp, key, None))

    def initscr(self):
        return self._screen


curses = Curses()
