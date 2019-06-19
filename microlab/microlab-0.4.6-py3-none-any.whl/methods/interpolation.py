from microlab.signals import Signal_1D, Signal_2D
from microlab.plots.__init__ import Plot_2D
from scipy.interpolate import interp1d
from numpy import linspace



class Cubic:
    x = []
    y = []
    values = [x, y]

    def __init__(self, signal=None, total_number=10, verbose=False):
        if signal is None:
            print('[!] can not interpolate None signal')
        elif type(signal) == Signal_1D:
            self.signal = signal
            x = self.signal.x
            y = self.signal.y
            self.x, self.y = self.cubic(x, y, total_number, verbose=verbose)
            # if verbose:
            #     print('Signal 1D found')
            #     print('New    X:{}'.format(len(self.x)))
            #     print('New    Y:{}'.format(len(self.y)))

        elif type(signal) == Signal_2D:
            self.signal = signal
            x = self.signal.x
            y = self.signal.y
            self.x, self.y = self.cubic(x, y, total_number, verbose=False)
            if verbose:
                print('Signal 2D found')
                print('New    X:{}'.format(len(self.x)))
                print('New    Y:{}'.format(len(self.y)))
        self.values = [self.x, self.y]

    def cubic(self, x, y, total_number, verbose=False):
        multiplier = total_number / len(x)
        if verbose:
            print(' Cubic interpolation', end=' ')
            print('X: {}, Y: {}'.format(x, y))

        xnew = self.generate_new_frames(x, multiplier)
        f = interp1d(x, y, kind='cubic')
        ynew = f(xnew)
        ynew = ynew.tolist()
        return xnew, ynew

    def generate_new_frames(self, x, multiplier, verbose=False):
        total_points = len(x) * multiplier
        xnew = linspace(0, len(x) - 1, num=total_points, endpoint=True)
        if verbose:
            print('generated {} frames '.format(total_points - len(x)))
        return xnew

    def show_coordinates(self):
        print('X: {}'.format(self.x))
        print('Y: {}'.format(self.y))

    def show(self, title='Interpolation', marker='.'):
        Plot_2D(signal=self, title=title, marker=marker)

    def get_x(self, index):
        return self.x[index]

    def get_y(self, index):
        return self.y[index]

    def get_point(self, index):
        return self.get_x(index=index), self.get_y(index=index)

    def length_x(self):
        return len(self.x)

    def length_y(self):
        return len(self.y)