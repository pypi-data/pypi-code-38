import pytest

from parameters import CategoryParameter, RangeParameter, Parameter
from evaluator import EvaluatorSR
from problem import Problem
import optimizer
import numpy as np

from platypus.config import PlatypusConfig
import random

@pytest.fixture
def parameters():
    parameters=[Parameter(value_descriptor=CategoryParameter(list(range(80,90))), name='1st'),
            Parameter(value_descriptor=CategoryParameter(list(range(80,90))), name='2nd'),
            Parameter(value_descriptor=RangeParameter(3, 100), name='3rd')
           ]
    return parameters


def mixed_types(vals):
    #helper function from the jupyter notebook
    vals = list(vals)
    num = vals.pop(-1)
    objectives = tuple(num % v for v in vals)
    return (objectives,())


def test_mixed_type_parameters(parameters):
    """to make sure that we can use different parameter types in the same algorithms while still getting optimal outputs"""

    evaluator = EvaluatorSR(mixed_types, Problem(parameters, 2))
    random.seed(1)
    results = optimizer.EpsMOEA(evaluator, epsilons=10)

    value = results.iloc[0]['outputs_0']
    print(value)
    assert np.isclose(value, 0.4451952793850751), f'Unexpected output: {value}'

    assert 1

def test_optimizer_customization(parameters):
    """testing the variator field while using mixed parameters"""

    evaluator = EvaluatorSR(mixed_types, Problem(parameters, 2))
    variator = optimizer.get_operator(evaluator.to_platypus())

    random.seed(2)
    results = optimizer.EpsMOEA(evaluator, variator=variator, epsilons=10)

    value = results.iloc[0]['outputs_1']
    print(value)
    assert np.isclose(value, 0.4607928200940279), f'Unexpected output: {value}'

    assert 1
