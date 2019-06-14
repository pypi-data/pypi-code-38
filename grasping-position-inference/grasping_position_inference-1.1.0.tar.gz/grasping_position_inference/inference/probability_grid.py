import numpy as np
MIN_X = -1.3
MIN_Y = -1.3
MAX_X = 1.3
MAX_Y = 1.3
STEP_SIZE = 0.01


INIT_PROBABILITY = 0.0


class ProbabilityGrid(object):
    def __init__(self):
        self._grid = _init_grid()

    def __getitem__(self, key):
        x, y = _transform_key_to_grid_coordinates(key)
        return self._grid[y][x]

    def __setitem__(self, key, value):
        x, y = _transform_key_to_grid_coordinates(key)
        self._grid[y][x] = value

    def update(self, predictor):
        inference_result = predictor.get_probability_distribution_for_grid()

        min_x, min_y, max_x, max_y = predictor._min_x, predictor._min_y, predictor._max_x, predictor._max_y
        x_steps = _steps(min_x, max_x)
        y_steps = _steps(min_y, max_y)
        print ''
        for x in range(0, x_steps+1):
            current_x = min_x + (x*STEP_SIZE)
            for y in range(0, y_steps+1):
                current_y = min_y + (y*STEP_SIZE)
                self[current_x, current_y] = inference_result[y][x]

    def get_grid(self):
        norm = np.sum(self._grid)
        if norm > 0.0:
            return np.divide(self._grid, norm)
        else:
            return self._grid


def _init_grid():
    dimension = _steps(-1.3, 1.3)
    dimension = dimension + 1

    return np.full((dimension, dimension), INIT_PROBABILITY)


def _steps(start, end):
    biggest = abs(end)
    smallest = abs(start)

    if smallest > biggest:
        temp = smallest
        smallest = biggest
        biggest = temp

    if np.sign(start) == np.sign(end):
        distance = biggest - smallest
    else:
        distance = biggest + smallest

    return int(round(distance / STEP_SIZE, 0))


def _transform_key_to_grid_coordinates(key):
    x = _steps(MIN_X, key[0])
    y = _steps(key[1], MAX_Y)

    return x, y