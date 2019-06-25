import pytest

import eppy_funcs as ef
from evaluator import EvaluatorEP
from parameters import RangeParameter, CategoryParameter, Parameter, FieldSelector, expand_plist
from problem import EPProblem, Problem
import platypus
import optimizer
from objectives import MeterReader
import sampling
import random
import numpy as np

#This test takes about 3-4 minutes to run so you can omit it by running pytest_short.py instead of pytest

@pytest.fixture
def parameters():
    parameters = expand_plist(
        {'NonRes Fixed Assembly Window':
        {'UFactor':(0.1,5),
        'Solar Heat Gain Coefficient':(0.01,0.99)
        },
        'Mass NonRes Wall Insulation':{'Thickness':(0.01,0.09)},
        })
    return parameters


@pytest.fixture
def problem(parameters):
    objectives = ['Electricity:Facility', 'Gas:Facility']
    return EPProblem(parameters, objectives)


def test_flexibility(problem):
    """to make sure that you can use multiple algorithms on the same data set"""

    idf = ef.get_idf()
    evaluator = EvaluatorEP(problem, idf)

    random.seed(1)
    #run the first algorithm
    platypus_problem = evaluator.to_platypus()
    algorithm = platypus.NSGAII(problem=platypus_problem, population_size=5)
    algorithm.run(5)

    #run the second algorithm
    generator = platypus.InjectedPopulation(algorithm.population)
    alg2 = platypus.EpsMOEA(problem=platypus_problem, generator=generator, epsilons=3, population_size=5)
    alg2.run(5)

    results = optimizer.solutions_to_df(alg2.result, problem, parts=['inputs', 'outputs'])

    value = results.iloc[0]['Electricity:Facility']
    assert np.isclose(value, 1747893172.6172004), f'Unexpected result: {value}'
    assert all([optimal == True for optimal in results['pareto-optimal']]), f'Algorithm not producing optimal outputs'

    #change this to 0 to see stdout and stderr
    assert 1
