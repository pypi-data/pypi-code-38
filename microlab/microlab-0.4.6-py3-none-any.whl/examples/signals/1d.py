from microlab.signals import Signal_1D
from microlab import samples
from microlab.types import is_1d_signal

def test_from_list_to_signal():
    print('[  I  ]  Signal 1D', end='.....')
    signal_1_from_list = Signal_1D(values=samples.List_b, verbose=False)
    if is_1d_signal(object=signal_1_from_list):
        print('[ OK ]   identify Signal 1D using List')
        # signal_1_from_list.show_coordinates()
    else:
        print('[ !! ]   identify Signal 1D using List')

def test_from_tuple_to_signal():
    print('[  I  ]  Signal 1D', end='.....')
    signal_1_from_tuple = Signal_1D(values=samples.Tuple_b, verbose=False)
    if is_1d_signal(object=signal_1_from_tuple):
        print('[ OK ]   identify Signal 1D using Tuple')
        # signal_1_from_tuple.show_coordinates()
    else:
        print('[ !! ]     identify Signal 1D using Tuple')

def test_from_nmArray_to_signal():
    print('[  I  ]  Signal 1D', end='.....')
    signal_1_from_npArray = Signal_1D(values=samples.npArray_a, verbose=False)
    if is_1d_signal(object=signal_1_from_npArray):
        print('[ OK ]   identify Signal 1D using Numpy Array')
        # signal_1_from_npArray.show_coordinates()
    else:
        print('[ !! ]   identify Signal 1D using Numpy Array')


if __name__ == "__main__":
    print('\n ~ TEST 1D SIGNALS ~')
    test_from_list_to_signal()
    test_from_tuple_to_signal()
    test_from_nmArray_to_signal()



