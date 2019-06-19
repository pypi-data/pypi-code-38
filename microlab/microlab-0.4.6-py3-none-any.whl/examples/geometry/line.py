from microlab.signals import Signal_2D
from microlab.samples.__init__ import dataset_npArray
from microlab.geometry.lines import create_line


if __name__ == '__main__':
    signal = Signal_2D(values=dataset_npArray, verbose=False)
    line = create_line(signal=signal, verbose=True)
    print(line)
