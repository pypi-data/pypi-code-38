from microlab.signals import Signal_1D, Signal_2D
from microlab.methods.intersection import Intersection
from microlab.methods.interpolation import Cubic
from microlab import samples

if __name__ == '__main__':
    # Data
    # Data.show()

    # 1D Signals
    # signal_1 = Signal_1D(values=Data.x1, serialized=False, verbose=False)
    # signal_2 = Signal_1D(values=Data.x2, serialized=False, verbose=False)
    # signal_1.show(title='Signal 1 using "x1" io', marker='o')
    # signal_2.show(title='Signal 2 using "x2" io', marker='o')

    # 2D Signals
    signal_1 = Signal_2D(values=data.dataset_1, verbose=False)
    signal_2 = Signal_2D(values=data.dataset_2, verbose=False)
    # signal_1.show(title='signal 1 using "x1" and "y1" io', marker='-')
    # signal_2.show(title='signal 2 using "x2" and "y2" io', marker='-')


    # Intersection
    intersections = Intersection(signal_a=signal_1, signal_b=signal_2, verbose=False)
    if len(intersections.points) > 0:
        intersections.show(title='intersection node ', marker='or')

    # interpolation
    s1 = Signal_1D(values=signal_1.x, serialized=True, verbose=False)
    i1 = Cubic(signal=s1, total_number=10, verbose=False)
    s1_interpolated = Signal_2D(values=i1.values,  verbose=True)
    s1_interpolated.show(title='s1 Interpolated" ', marker='.')


    s2_1d = Signal_1D(values=signal_2.x, serialized=True, verbose=True)
    i2 = Cubic(signal=s2_1d, total_number=10, verbose=False)
    s2_interpolated = Signal_2D(values=i2.values, verbose=True)
    s2_interpolated.show(title='s2 Interpolated ', marker='.')


    intersections = Intersection(signal_a=s1_interpolated, signal_b=s2_interpolated, verbose=True)
    if len(intersections.points) > 0 :
        intersections.show(title='intersection node ', marker='or')
