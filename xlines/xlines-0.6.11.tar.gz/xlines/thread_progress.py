import sys
import threading
import time

# progress bar
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts.progress_bar import formatters


tab = '\t'.expandtabs(8)

style = Style.from_dict({
    '': 'orange',
})


custom_formatters = [
    formatters.Text(tab),
    formatters.Label(suffix=': '),
    formatters.Bar(start=' |', end='|', sym_a='#', sym_b='#', sym_c='.'),
    formatters.Text(' '),
    formatters.Progress(),
    formatters.Text(' '),
    formatters.Percentage(),
    formatters.Text(' [elapsed: '),
    formatters.TimeElapsed(),
    formatters.Text(' left: '),
    formatters.TimeLeft(),
    formatters.Text(']'),
    formatters.Text(tab),
]


class ProgressBarThread(threading.Thread):
    def __init__(self, label='Working', delay=0.1, cycles=500):
        super(ProgressBarThread, self).__init__()
        self.label = label
        self.delay = delay  # interval between updates
        self.running = False
        self.end = int(cycles)

    def start(self):
        self.running = True
        super(ProgressBarThread, self).start()

    def run(self):
        with ProgressBar(style=style, formatters=custom_formatters) as pb:
            for i in pb(range(self.end), label=self.label):
                time.sleep(self.delay)
                if not self.running:
                    break

    def stop(self):
        self.running = False
        self.join()  # wait for run() method to terminate
        sys.stdout.write('\r' + len(self.label)*' ' + '\r')  # clean-up
        sys.stdout.flush()


class SpinnerThread(threading.Thread):
    def __init__(self, label='Working', delay=0.2):
        super(ProgressBarThread, self).__init__()
        self.label = label
        self.delay = delay  # interval between updates
        self.running = False

    def start(self):
        self.running = True
        super(ProgressBarThread, self).start()

    def run(self):
        label = '\r' + self.label + ' '
        while self.running:
            for c in ('-', '\\', '|', '/'):
                sys.stdout.write(label + c)
                sys.stdout.flush()
                time.sleep(self.delay)

    def stop(self):
        self.running = False
        self.join()  # wait for run() method to terminate
        sys.stdout.write('\r' + len(self.label)*' ' + '\r')  # clean-up
        sys.stdout.flush()
