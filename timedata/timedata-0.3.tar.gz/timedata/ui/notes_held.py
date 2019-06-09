from kivy import graphics
from kivy.uix.widget import Widget
import math
import threading

PADDING = 4


class NotesHeld(Widget):
    def __init__(
        self,
        columns=16,
        low=0,
        high=127,
        padding=PADDING,
        color=(1, 1, 1),
        frame_padding=4,
        shape=graphics.Ellipse,
        **kwds
    ):
        super().__init__(**kwds)
        assert high >= low
        self.low = low
        self.high = high
        self.columns = columns
        self.rows = math.ceil((high - low + 1) / columns)
        self.padding = padding
        self.shape = shape
        self.frame_padding = frame_padding
        self.color = color
        self.notes_held = {}
        self.note_position = {}
        self.note_size = 0, 0
        self.lock = threading.RLock()

    def on_size(self, *args):
        with self.lock:
            self._compute_note_positions()
            self._rewrite_notes()

    def clear(self):
        with self.lock:
            self.notes_held.clear()
            self._rewrite_notes()

    def note(self, note, is_on, count=1):
        if self.low <= note <= self.high:
            with self.lock:
                self._add_note(note, is_on, count)

    def _add_note(self, note, is_on, count):
        counter = self.notes_held.setdefault(note, _NoteCounter())
        counter.count += count * (1 if is_on else -1)

        if not counter.element:
            pos = self.note_position[note]
            with self.canvas:
                counter.element = self.shape(pos=pos, size=self.note_size)

        elif counter.count <= 0:
            del self.notes_held[note]
            self.canvas.remove(counter.element)

    def _compute_note_positions(self):
        x, y = self.pos
        width, height = self.size
        w = (width - self.padding - self.frame_padding) // self.columns
        h = (height - self.padding - self.frame_padding) // self.rows
        m = min(w, h)
        if not m:
            return

        dx = x + (width - m * self.columns + self.padding) // 2
        dy = y + (height - m * self.rows + self.padding) // 2
        size = m - self.padding
        self.note_size = size, size

        for note in range(self.low, self.high + 1):
            ny, nx = divmod(note - self.low, self.columns)
            self.note_position[note] = dx + nx * m, dy + ny * m

    def _rewrite_notes(self):
        self.canvas.clear()
        with self.canvas:
            graphics.Color(*self.color)

        notes_held, self.notes_held = self.notes_held, {}
        for note, counter in notes_held.items():
            self.note(note, True, counter.count)


class _NoteCounter:
    __slots__ = 'count', 'element'

    def __init__(self):
        self.count = 0
        self.element = None
