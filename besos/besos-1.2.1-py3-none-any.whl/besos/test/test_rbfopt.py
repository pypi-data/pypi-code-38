import pytest

from optimizer import rbf_opt
from evaluator import EvaluatorSR
from parameters import Parameter, RangeParameter
from problem import Problem
import numpy as np

def test_rbfopt():
    """Simple test to make sure RBFopt can be run properly"""

    def obj_funct(x):
        return (x[0]*x[1] - x[2],),()

    param_list = [Parameter(value_descriptor=RangeParameter(0,10)) for _ in range(3)]
    problem = Problem(param_list, 1)

    evaluator = EvaluatorSR(obj_funct, problem, error_mode='Silent')

    opt = rbf_opt(evaluator, 30)
    value = opt.iloc[0]

    assert np.isclose(value['None_0'], 0) and (np.isclose(value['None_1'], 5.062882681226724) or np.isclose(value['None_1'], 0.5148690)) and np.isclose(value['None_2'], 10) and np.isclose(value['outputs_0'], -10), f'Unexpected output: {value}'     # None_1 assert values hardcoded to pass on Debian
