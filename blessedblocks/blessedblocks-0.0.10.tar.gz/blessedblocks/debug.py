from .block import Block, SizePref
from queue import Queue

# Needs work
debug_q = Queue()
class DebugBlock(Block):
    def __init__(self, name=None):
        super().__init__(name,
                         text='',
                         w_sizepref=SizePref(hard_min=0, hard_max=float('inf')),
                         h_sizepref=SizePref(hard_min=0, hard_max=float('inf')))
        self.count = 0
        self.lines = []
    def display(self, width, height, x, y, term=None):
        with self.write_lock:
            out = []
            for _ in range(debug_q.qsize()):
                self.lines.append(debug_q.get())
            for h in range(height):
                if h >= len(self.lines):
                    break
                if term:
                    with term.location(x=x, y=y+h):
                        self.count += 1
                        print(self.count, self.lines[h][:width], end='')
                else:
                    out.append(line)
            if not term:
                print(out, end='\n')

