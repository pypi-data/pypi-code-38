from microlab.signals import Signal_2D
from microlab import samples
from microlab.types import is_2d_signal

def test_plot_2d_list():
    print('| 2D List  |', end='-->')
    signal_from_list = Signal_2D(values=data.dataset_list, verbose=True)
    if is_2d_signal(object=signal_from_list):
        signal_from_list.show(title='Plot 2D List', marker='.')
    else:
        print('[!!]')

def test_plot_2d_tuple():
    print('| 2D Tuple |', end='-->')
    signal_from_tuple = Signal_2D(values=data.dataset_list, verbose=True)
    if is_2d_signal(object=signal_from_tuple):
        signal_from_tuple.show(title='Plot 2D Tuple', marker='.')
    else:
        print('[!!]')


def test_plot_2d_npArray(verbose=False):
    print('| 2D Array |', end=' ---->')
    signal_1_from_ndarray = Signal_2D(values=data.dataset_npArray, verbose=True)
    if is_2d_signal(object=signal_1_from_ndarray):
        signal_1_from_ndarray.show(title='Plot 2D Numpy Array', marker='.')
    else:
        print('[!!]')


if __name__ == "__main__":
    print('\n ~ TEST 2D PLOT ~')
    print('|  INPUT   |        DETECT        |   OBJECT SIGNAL CREATED              | DATA STRACTURE')
    test_plot_2d_list()
    test_plot_2d_tuple()
    test_plot_2d_npArray()

