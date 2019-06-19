from microlab.methods.intersection import Intersection
from microlab.signals import Signal_2D
from microlab import samples


def test_intersection_from_2D_signal():
    print(' Intersection from 2 Signals 2D', end='.....')

    # Signals
    signal_1 = Signal_2D(values=samples.dataset_1, verbose=False)
    signal_2 = Signal_2D(values=samples.dataset_2, verbose=False)

    # Intersection
    intersection = Intersection(signal_a=signal_1, signal_b=signal_2, verbose=False)
    intersection.show()
    # print(intersection.points)
    if len(intersection.points) == 1:
        print('[ OK ]   intersection from  2 x Signals 2D')
    else:
        print('[ !! ]   intersection from  2 x Signals 2D')




if __name__ == "__main__":
    print('\n ~ TEST INTERSECTION ~')
    test_intersection_from_2D_signal()


