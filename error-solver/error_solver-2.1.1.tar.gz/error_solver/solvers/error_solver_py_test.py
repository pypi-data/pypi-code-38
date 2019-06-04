import os
import time
import pytest
from ..data import get_file_path, _cylinder
from .error_solver_py import *
from .error_solver import *


def test_repr():
    solver = ErrorSolverPy.from_module(_cylinder)
    repr(solver)


def test_write_and_solve():
    solver = ErrorSolver.from_file(get_file_path('cylinder.ef'))
    path = get_file_path('_cylinder_test_mod.py')

    # Remove test module if it already exists
    if os.path.exists(path): # pragma: no cover
        os.remove(path)

    solver.write_python(path)
    time.sleep(3)

    from ..data import _cylinder_test_mod
    solver = ErrorSolverPy.from_module(_cylinder_test_mod)

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

    # Remove test module
    os.remove(path)


def test_solve():
    solver = ErrorSolverPy.from_module(_cylinder)

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


def test_bad_values():
    solver = ErrorSolverPy.from_module(_cylinder)

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
