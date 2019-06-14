import numpy as np


class Grid(object):
    def __init__(self, x_definition, y_definition):
        self._x_start, self._x_end, self._x_step_size = x_definition
        self._y_start, self._y_end, self._y_step_size = y_definition

        self._grid = self._create_grid()
        self.x = self._grid[0]
        self.y = self._grid[1]

    def _create_grid(self):

        x = np.arange(int(self._x_start*100), int((self._x_end + self._x_step_size) * 100), int(self._x_step_size*100))
        y = np.arange(int(self._y_start*100), int((self._y_end + self._y_step_size) * 100), int(self._y_step_size*100))

        x = np.divide(x, 100.)
        y = np.divide(y, 100.)

        return np.meshgrid(x, y)

