from microlab.signals import Signal_2D
from microlab import samples
from microlab.types import is_2d_signal


def test_from_list_to_signal():
    print('[  I  ]  Signal 2D ', end='.....')
    signal_1_from_list = Signal_2D(values=samples.dataset_list, verbose=False)
    if is_2d_signal(object=signal_1_from_list):
        print('[ OK ]   identify Signal 2D using List')
        # signal_1_from_list.show_coordinates()
    else:
        print('[ !! ]   identify Signal 2D using List')


def test_from_tuple_to_signal():
    print('[  I  ]  Signal 2D ', end='.....')
    signal_1_from_tuple = Signal_2D(values=samples.dataset_tuple, verbose=False)
    if is_2d_signal(object=signal_1_from_tuple):
        print('[ OK ]   identify Signal 2D using Tuple')
        # signal_1_from_tuple.show_coordinates()
    else:
        print('[!!]   identify Signal 2D using Tuple')

def test_from_nmArray_to_signal():
    print('[  I  ]  Signal 2D ', end='.....')
    signal_1_from_ndArray = Signal_2D(values=samples.dataset_npArray, verbose=False)
    if is_2d_signal(object=signal_1_from_ndArray):
        print('[ OK ]   identify Signal 2D using Numpy Array')
        # signal_1_from_ndArray.show_coordinates()
    else:
        print('[ !! ]   identify Signal 2D using Numpy Array')


if __name__ == "__main__":
    print('\n ~ TEST 2D SIGNALS ~')
    # print('\nData: \n   A:{}, \n   B:{}'.format(Data.a, Data.b))
    test_from_list_to_signal()
    test_from_tuple_to_signal()
    test_from_nmArray_to_signal()



