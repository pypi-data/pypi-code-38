from microlab.signals import Signal_1D
from microlab import samples
from microlab.types import is_1d_signal

def test_plot_1d_list():
    print('| 1D List  |', end=' ---->')
    signal_from_list = Signal_1D(values=samples.List_a, verbose=True)
    if is_1d_signal(object=signal_from_list):
        signal_from_list.show(title='Plot 1D List', marker='.')
    else:
        print('[!!]')

def test_plot_1d_tuple():
    print('| 1D Tuple |', end=' ---->')
    signal_from_tuple = Signal_1D(values=samples.Tuple_a, verbose=True)
    if is_1d_signal(object=signal_from_tuple):
        signal_from_tuple.show(title='Plot 1D Tuple', marker='.')
    else:
        print('[!!]')

def test_plot_1d_npArray():
    print('| 1D Array |', end=' ---->')
    signal_1_from_ndarray = Signal_1D(values=samples.npArray_a, verbose=True)
    if is_1d_signal(object=signal_1_from_ndarray):
        signal_1_from_ndarray.show(title='Plot 1D Numpy Array', marker='.')
    else:
        print('[!!]')


if __name__ == "__main__":
    print('\n ~ TEST 1D PLOT ~')
    print('|  INPUT   |        DETECT        |   OBJECT SIGNAL CREATED              | DATA STRACTURE')
    test_plot_1d_list()
    test_plot_1d_tuple()
    test_plot_1d_npArray()

