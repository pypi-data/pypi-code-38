from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty
import math


class IntEntry(TextInput):
    value = NumericProperty(0.0)

    def __init__(self, low=-math.inf, high=math.inf, **kwds):
        if low >= 10:
            # Because otherwise we couldn't ever type the first digit
            # TODO: figure out how to fix this
            raise ValueError('low must be less than 10')

        if low >= high:
            raise ValueError('Empty slider')

        self.low = low
        self.high = high
        digits = math.log10(max(abs(low), abs(high))) + 1
        self._width = int(min(digits, 12)) + (low < 0)
        super().__init__(multiline=False, **kwds)

    def insert_text(self, substring, from_undo=False):
        c = self.cursor[0]
        text = self.text[:c] + substring + self.text[c:]
        if self._validate(text):
            super().insert_text(substring, from_undo=from_undo)

    def on_text(self, _, text):
        self.value = int(text or '0')

    def on_value(self, _, value):
        self.text = str(value)

    def _validate(self, text):
        if text == '' or self.low < 0 and text == '-':
            return True
        try:
            return self.low <= int(text) <= self.high
        except Exception:
            pass


class IntEntry2(TextInput):
    value = NumericProperty(0.0)

    def __init__(self, low=-math.inf, high=math.inf, **kwds):
        if low >= 10:
            # Because otherwise we couldn't ever type the first digit
            # TODO: figure out how to fix this
            raise ValueError('low must be less than 10')

        if low >= high:
            raise ValueError('Empty slider')

        self.low = low
        self.high = high
        digits = math.log10(max(abs(low), abs(high))) + 1
        self._width = int(min(digits, 12)) + (low < 0)
        super().__init__(multiline=False, **kwds)

    def insert_text(self, substring, from_undo=False):
        c = self.cursor[0]
        text = self.text[:c] + substring + self.text[c:]
        if self._validate(text):
            super().insert_text(substring, from_undo=from_undo)

    def on_text(self, _, text):
        self.value = int(text or '0')

    def on_value(self, _, value):
        self.text = str(value)

    def _validate(self, text):
        if text == '' or self.low < 0 and text == '-':
            return True
        try:
            return self.low <= int(text) <= self.high
        except Exception:
            pass
