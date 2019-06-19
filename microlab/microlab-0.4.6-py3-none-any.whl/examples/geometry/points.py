from microlab.signals import Signal_2D
from microlab.samples.__init__ import dataset_npArray

from microlab.geometry.points import create_points

if __name__ == '__main__':
    signal = Signal_2D(values=dataset_npArray, verbose=False)
    points = create_points(signal=signal, verbose=True)
    print(points)
