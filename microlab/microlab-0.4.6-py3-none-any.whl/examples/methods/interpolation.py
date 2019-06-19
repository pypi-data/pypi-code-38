from microlab.signals import Signal_1D, Signal_2D
from microlab.methods.interpolation import Cubic
from microlab import samples


def test_interpolation_cubic_from_1D_signal():
    print('[  I  ]  Interpolation from Signal 1D', end='.....')
    signal_1 = Signal_1D(values=samples.List_a, serialized=True, verbose=False)
    total_numbers = 100
    cubic_1d = Cubic(signal=signal_1, total_number=total_numbers, verbose=False)
    cubic_1d.show(title="Cubic interpolation 1D", marker='.')
    if len(cubic_1d.y) == total_numbers and len(cubic_1d.x) == total_numbers:
        print('[ OK ]   interpolate Signal 1D')
    else:
        print('[ !! ]   interpolate Signal 1D')


def test_interpolation_cubic_from_2D_signal():
    print('[  I  ]  Interpolation from Signal 2D', end='.....')
    signal_1 = Signal_2D(values=samples.dataset_list, verbose=False)
    total_numbers = 100
    cubic_2d = Cubic(signal=signal_1, total_number=total_numbers, verbose=False)
    cubic_2d.show(title="Cubic interpolation 2D", marker='.')
    if len(cubic_2d.y) == total_numbers and len(cubic_2d.x) == total_numbers:
        print('[ OK ]   interpolate Signal 2D')
    else:
        print('[ !! ]   interpolate Signal 2D')


if __name__ == "__main__":
    print('\n ~ TEST INTERPOLATION CUBIC ~')
    test_interpolation_cubic_from_1D_signal()
    test_interpolation_cubic_from_2D_signal()
