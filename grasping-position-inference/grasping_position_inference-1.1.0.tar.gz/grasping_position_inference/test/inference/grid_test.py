from grasping_position_inference.inference.grid import Grid


def test_should_return_valid_grid():
    x_parameters = (0.0, 0.8, 0.01)
    y_parameters = (0.0, 0.8, 0.01)

    grid = Grid(x_parameters, y_parameters)

    assert len(grid._grid[0]) == 81
    assert len(grid._grid[1]) == 81

    x_parameters = (-0.8, 0., 0.01)
    y_parameters = (-0.8, 0., 0.01)

    grid = Grid(x_parameters, y_parameters)

    assert len(grid._grid[0]) == 81
    assert len(grid._grid[1]) == 81

    assert grid._grid[0][0][0] == -0.8
    assert grid._grid[1][-1][0] >= 0.