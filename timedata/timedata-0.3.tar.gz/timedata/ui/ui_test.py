from . import bang
from . import int_entry
from . import int_slider
from . import notes_held
from . import selector
from . import switch_button
from kivy.app import App
from timedata.instruments.laser import constants
import random
import threading
import time


class UIApp(App):
    def build(self):
        if not False:
            return test_int_slider()
        if False:
            return test_bang()
        if False:
            return test_switch_button()
        if False:
            return test_notes_held()
        if False:
            return test_selector()
        if False:
            return test_int_entry()


def test_int_entry():
    b = int_entry.IntEntry(0, 100000)
    b.bind(value=print)
    return b


def test_int_slider():
    return int_slider.IntSlider('IntSlider', 0, 255)


def test_selector():
    s = selector.Selector(constants.Patterns, size_hint=(0.5, 0.1))
    s.bind(enum=print)
    return s


def test_bang():
    b = bang.Bang('Bang!', 0.5)

    def sb(t):
        time.sleep(t)
        b.bang()

    def target():
        sb(1)
        sb(2)
        sb(0.4)
        sb(0.4)
        sb(0.4)
        sb(2)
        sb(0.6)
        sb(0.6)
        sb(0.6)

    threading.Thread(target=target, daemon=True).start()
    return b


def test_switch_button():
    return switch_button.SwitchButton('Hello', 'world')


def test_notes_held():
    import math

    high = 14
    held = notes_held.NotesHeld(
        high=high, columns=int(math.sqrt(high)), color=(0.5, 0.5, 0.5)
    )

    def target():
        while True:
            time.sleep(random.uniform(0.05, 0.5))
            note = random.randrange(high + 1)
            held.note(note, note not in held.notes_held)

    threading.Thread(target=target, daemon=True).start()
    return held


if __name__ == '__main__':
    UIApp().run()
