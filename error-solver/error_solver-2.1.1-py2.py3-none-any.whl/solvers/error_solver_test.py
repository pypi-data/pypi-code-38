import os
import time
import pytest
from ..data import get_file_path
from .error_solver import *


def test_repr():
    path = get_file_path('wire_load.ef')
    solver = ErrorSolver.from_file(path)
    repr(solver)


def test_from_file():
    path = get_file_path('wire_load.ef')
    solver = ErrorSolver.from_file(path)

    assert len(solver.get_equations()) == 4
    assert len(solver.get_partials()) == 4


def test_get_equations():
    path = get_file_path('wire_load.ef')
    solver = ErrorSolver.from_file(path)

    assert len(solver.get_equations('wind_pressure')) == 3
    assert len(solver.get_equations('wind_velocity')) == 4


def test_get_partials():
    path = get_file_path('wire_load.ef')
    solver = ErrorSolver.from_file(path)

    assert len(solver.get_partials('wind_pressure')) == 3
    assert len(solver.get_partials('wind_velocity')) == 4


def test_check_determinancy1():
    path = get_file_path('cylinder.ef')
    solver = ErrorSolver.from_file(path)

    values = {
        'height': 12,
        'radius': 5,
        'area': 78.539816,
        'volume': 942.477796
    }

    errors = {
        'height': 0.05,
    }

    with pytest.raises(ValueError):
        solver.solve(values, errors)


def test_check_determinancy2():
    path = get_file_path('cylinder.ef')
    solver = ErrorSolver.from_file(path)

    values = {
        'height': 12,
        'radius': 5,
        'area': 78.539816,
        'volume': 942.477796
    }

    errors = {
        'height': 0.05,
        'radius': 0.05,
        'area': 0.05,
    }

    with pytest.raises(ValueError):
        solver.solve(values, errors)


def test_solve1():
    path = get_file_path('cylinder.ef')
    solver = ErrorSolver.from_file(path)

    values = {
        'height': 12,
        'radius': 5,
        'area': 78.539816,
        'volume': 942.477796
    }

    errors = {
        'height': 0.05,
        'radius': 0.05
    }

    df = solver.solve(values, errors)
    assert pytest.approx(df['value']['volume'], 0.01) == 942.477796
    assert pytest.approx(df['error']['volume'], 0.01) == 22.78
    assert pytest.approx(df['pct_error']['volume'], 0.01) == 2.42
    assert df['is_calc']['volume'] == True


def test_solve2():
    path = get_file_path('cylinder.ef')
    solver = ErrorSolver.from_file(path)

    values = {
        'height': 12,
        'radius': 5,
        'area': 78.539816,
        'volume': 942.477796
    }

    errors = {
        'height': 0.05,
        'radius': 0.05
    }

    const = {
        'height': 0
    }

    df = solver.solve(values, errors, const)
    assert pytest.approx(df['value']['volume'], 0.01) == 942.477796
    assert pytest.approx(df['error']['volume'], 0.01) == 22.78
    assert pytest.approx(df['pct_error']['volume'], 0.01) == 2.42
    assert df['is_calc']['volume'] == True


def test_write_python():
    path = get_file_path('wire_load.ef')
    solver = ErrorSolver.from_file(path)
    path = get_file_path('_wire_load_test_mod.py')

    solver.write_python(path)
    time.sleep(3)

    assert os.path.exists(path)
    os.remove(path)


def test_bad_values():
    path = get_file_path('cylinder.ef')
    solver = ErrorSolver.from_file(path)

    values = {
        'height': 12,
        'radius': 5,
        'area': 78.539816,
        'volume': 900
    }

    errors = {
        'height': 0.05,
        'radius': 0.05
    }

    with pytest.raises(ValueError):
        solver.solve(values, errors)


def test_missing_values():
    path = get_file_path('cylinder.ef')
    solver = ErrorSolver.from_file(path)

    values = {
        'height': 12,
        'radius': 5,
        'area': 78.539816,
    }

    errors = {
        'height': 0.05,
        'radius': 0.05
    }

    with pytest.raises(ValueError):
        solver.solve(values, errors)



def test_restricted_symbols():
    equations = [
        'V = I * R'
    ]

    values = {
        'I': 1,
        'R': 2,
        'V': 2,
    }

    errors = {
        'I': 0.05,
        'R': 0.05,
    }

    solver = ErrorSolver(equations)

    with pytest.raises(ValueError):
        solver.solve(values, errors)
