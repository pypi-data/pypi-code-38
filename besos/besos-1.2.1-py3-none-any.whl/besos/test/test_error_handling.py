import pytest
import pandas as pd
from pandas import DataFrame as DF
import numpy as np

import eppy_funcs as ef
from evaluator import EvaluatorEP, EvaluatorSR
from parameters import RangeParameter, CategoryParameter, Parameter, FieldSelector
from problem import EPProblem
import sampling

#Some code taken and adapted from example notebooks, made to work through pytest

@pytest.fixture
def building():
    return ef.get_building()


@pytest.fixture
def problem():
    problem = EPProblem([
        Parameter(
            FieldSelector(object_name='Mass NonRes Wall Insulation', field_name='Thickness'),
            RangeParameter(min_val = 0.01, max_val=0.99)),
        Parameter(
            FieldSelector(class_name='Construction', object_name='ext-slab', field_name='Outside Layer'),
            CategoryParameter(options=('HW CONCRETE', 'Invalid Material')))])
    return problem


@pytest.fixture
def samples(problem):
    #seeded_sampler results in indexes 0-3 being Invalid Material and 4 being HW CONCRETE
    samples = sampling.dist_sampler(sampling.seeded_sampler, problem, 5)
    return samples


def test_exception_throwing(building, problem, samples):
    """test to make sure exceptions are thrown or ignored depending on the error_mode"""

    #check that an exception is raised with FailFast mode
    with pytest.raises(Exception):
        evaluator = EvaluatorEP(problem, building, error_mode='FailFast').df_apply(samples)

    #check that no exceptions are raised in the other mode
    try:
        evaluator = EvaluatorEP(problem, building, error_mode='Silent').df_apply(samples)
    except Exception as e:
        assert 0

    #change this to 0 to see stdout and stderr
    assert 1


def test_error_values(building, problem, samples):
    """check that automatic error handling will assign the desired error values"""

    #check that the default error value is assigned to invalid materials
    evaluator = EvaluatorEP(problem, building, error_mode='Silent')
    results = evaluator.df_apply(samples)
    value = results.iloc[0]['Electricity:Facility']
    assert value == np.inf, f'Invalid material not assigned the default error value, value assigned was: {value}'

    #check that a custom error value is assigned to invalid materials
    error_value=((-1,), ())
    evaluator = EvaluatorEP(problem, building, error_mode='Silent', error_value=error_value)
    results = evaluator.df_apply(samples)
    value = results.iloc[0]['Electricity:Facility']
    assert value == -1, f'Invalid material not assigned the correct error value, value assigned was: {value}'

    #check that valid inputs aren't assigned error values
    value = results.iloc[4]['Electricity:Facility']
    assert value != -1, f'Valid material was assigned the error value: {error_value}'

    #change this to 0 to see stdout and stderr
    assert 1
