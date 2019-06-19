from __future__ import print_function

from numpy import ndarray, asarray
from microlab.plots.__init__ import Plot_1D, Plot_2D

types = [
            tuple,
            list,
            ndarray
        ]


class Signal_1D:
    x = []
    y = []
    values = [x, y]

    def __init__(self, values=[], serialized=False, verbose=False):
        if values is None:
            print('[!] cannot create a 1D Signal with None values. ')

        # input values is list
        elif type(values) in [list]:
            if serialized:
                self.x = []
                self.y = []
                for x, y in enumerate(values):
                    self.x.append(x)
                    self.y.append(y)
            else:
                self.x = values
                self.y = self.timelapse(table=values)
            if verbose:
                print('[ List    ]---->| {} [ X: {}, Y:{} ]'.format(type(self), len(self.x), len(self.y)))
                # print(self.x)
                # print(self.y)

        # input values is tuple
        elif type(values) in [tuple]:
            if serialized:
                for x, y in enumerate(values):
                    self.x.append(x)
                    self.y.append(y)
            else:
                self.x = values
                self.y = self.timelapse(table=values)
            if verbose:
                print('[ Tuple   ]---->| {} [ X: {}, Y:{} ]'.format(type(self), len(self.x), len(self.y)))

        # input values is ndarray
        elif type(values) in [ndarray]:
                self.x = asarray(values)
                self.y = self.timelapse(table=values)

                if verbose:
                    print('[ ndArray ]---->| {} [ X: {}, Y:{} ]'.format(type(self), len(self.x), len(self.y)))

        # create signal values
        self.values = [self.x, self.y]

    def timelapse(self, table):
        t = []
        for i in range(len(table)):
            t.append(i)
        return t

    def show_coordinates(self):
        print('X: {}'.format(self.x))
        print('Y: {}'.format(self.y))

    def show(self, title='Signal 1D', marker='.'):
        Plot_1D(signal=self, title=title, marker=marker)

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


class Signal_2D:
    x = []
    y = []
    values = [x, y]

    def __init__(self, values=[], time=None, verbose=False):
        if values is None:
            print('[!] cannot create a 2D Signal with None values. ')

        # values has this shape [ [x1, x2], [y1, y2] ]
        if len(values) == 2:
            self.values = values
            self.y = values[0]
            self.x = values[1]

        # values has this shape [x1, x2, x3]
        # time   has this shape [y1, y2, y3]
        elif not time is None:
            self.y = values
            self.x = time

        #  values are tuple or list
        if type(values) in [tuple, list]:
            if verbose:
                print('[ List or Tuple ]->| {} [ X: {}, Y:{} ]'.format(type(self), len(self.x), len(self.y)))

        #  values are ndarrays
        elif type(values) in [ndarray]:
            if verbose:
                print('[ ndArray ]---->| {} [ X: {}, Y:{} ]'.format(type(self), len(self.x), len(self.y)))

        self.values = [self.x, self.y]

    def show_coordinates(self):
        print('X: {}'.format(self.x))
        print('Y: {}'.format(self.y))

    def show(self, title='Signal 2D', marker='.'):
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
