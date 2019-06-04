import pytest
from ..data import get_file_path
from .pipeline import *
from .error_solver import ErrorSolver

def test_solve():
    solvers = [
        ErrorSolver.from_file(get_file_path('area.ef')),
        ErrorSolver.from_file(get_file_path('volume.ef')),
    ]

    links = [
        {'area': 'area'}
    ]

    values = [
        {'radius': 5, 'area': 78.539816},
        {'height': 12, 'area': 78.539816, 'volume': 942.477796},
    ]

    errors = [
        {'radius': 0.05},
        {'height': 0.05},
    ]

    pipe = SolverPipeline(solvers, links)
    df = pipe.solve(values, errors)

    assert pytest.approx(df['value']['volume'], 0.01) == 942.477796
    assert pytest.approx(df['error']['volume'], 0.01) == 22.78
    assert pytest.approx(df['pct_error']['volume'], 0.01) == 2.42
    assert df['is_calc']['volume'] == True
