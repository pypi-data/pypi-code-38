import pytest
import pandas as pd
from pandas import DataFrame as DF
import numpy as np

from sklearn import svm, pipeline, linear_model
from sklearn.preprocessing import StandardScaler

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
def parameters():
    parameters = [
        Parameter(FieldSelector(object_name='NonRes Fixed Assembly Window',
                field_name='Solar Heat Gain Coefficient'),
                value_descriptor=RangeParameter(0.01,0.99)),
        Parameter(FieldSelector('Lights', '*', 'Watts per Zone Floor Area'),
                value_descriptor=RangeParameter(8, 12),
                name='Lights Watts/Area')]
    return parameters


@pytest.fixture
def problem(parameters):
    objectives = ['Electricity:Facility']
    problem = EPProblem(parameters, objectives)
    return problem


@pytest.fixture
def samples(problem):
    samples = sampling.dist_sampler(sampling.seeded_sampler, problem, 10)
    return samples


def test_expected_values(building, problem, samples):
    """check that the obtained results are consistent when using the same inputs"""

    def get_plot_data(model, density):
        #helper function from the example notebook
        p1 = problem.inputs[0].value_descriptor
        a = np.linspace(p1.min, p1.max, density)
        p2 = problem.inputs[1].value_descriptor
        b = np.linspace(p2.min, p2.max, density)
        plot_data = pd.DataFrame(np.transpose([np.tile(a, len(b)), np.repeat(b, len(a))]),
            columns=problem.names('inputs'))
        return pd.concat([plot_data, pd.Series(model.predict(plot_data))], axis=1)

    evaluator = EvaluatorEP(problem, building, error_mode='Silent')
    train = evaluator.df_apply(samples, keep_input=True)
    print(problem.names())
    x,y,c = problem.names()

    #train and get the values
    model = pipeline.make_pipeline(
        StandardScaler(),
        linear_model.Ridge())
    model.fit(train[[x, y]].values, train[c].values)
    density = 30
    df = get_plot_data(model, int(density*1.5))

    #check to see if the extremes and the midpoint are the expected values
    assert np.isclose([df.iloc[0][0]], [1592469368.6909447]), f'Unexpected value for low extreme'
    assert np.isclose([df.iloc[2024][0]], [2122632827.9627075]), f'Unexpected value for high extreme'
    assert np.isclose([df.iloc[1012][0]], [1857551098.326826]), f'Unexpected value for midpoint'

    #change this to 0 to see stdout and stderr
    assert 1
