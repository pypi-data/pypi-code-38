import pytest

import eppy_funcs as ef
from evaluator import EvaluatorEP, EvaluatorSR, EvaluatorEH
import numpy as np
import pandas as pd
from parameters import RangeParameter, CategoryParameter, Parameter, FieldSelector
from problem import EPProblem, Problem, EHProblem
import pyehub_funcs as pf
import sampling

@pytest.fixture
def building():
    #returns the basic building
    return ef.get_building()

@pytest.fixture
def hub():
    #returns the basic hub
    return pf.get_hub()

@pytest.fixture
def problem():
    parameters = [Parameter(FieldSelector(object_name='Mass NonRes Wall Insulation', field_name='Thickness'))]
    objectives = ['Electricity:Facility', 'Gas:Facility'] # the default is just 'Electricity:Facility'

    problem=EPProblem(parameters, objectives) #EPP Problem automatically converts these to MeterReaders
    return problem

@pytest.fixture
def energyhub_df():
    df = pd.DataFrame(np.array([[200, 600],[600, 200]]),columns= ['p1','p2'])
    return df

@pytest.fixture
def energyplus_df():
    df = EPdf = pd.DataFrame(np.array([[0.5],[0.8]]),columns= ['p1'])
    return df

@pytest.fixture
def hub_problem():

    parameters = [['LINEAR_CAPITAL_COSTS','Boiler'],['LINEAR_CAPITAL_COSTS','CHP']]
    objectives = ['total_cost','total_carbon']

    problem = EHProblem(parameters, objectives)
    return problem

def test_evaluatorEP(building, problem):
    """To make sure EvaluatorEP can be initialised and works as intended"""

    evaluator = EvaluatorEP(problem, building)
    result = evaluator([0.5]) # run with thickness set to 0.5

    assert np.isclose(result[0], 1818735943.9307632) and np.isclose(result[1], 2172045529.871896), f'Unexpected result for EvaluatorEP, {result}'
    #change this to 0 to see stdout and stderr
    assert 1


def test_evaluatorEH_single(hub, hub_problem):
    """To make sure EvaluatorEH can be initialised and works as intended"""
    
    evaluator = EvaluatorEH(hub_problem,hub)
    result = evaluator([200, 600])

    assert np.isclose(result[0], 1256.12) and np.isclose(result[1], 53.2299), f'Unexpected result for EvaluatorEH, {result}'
    #change this to 0 to see stdout and stderr
    assert 1

def test_evaluatorEH_df(hub, hub_problem, energyhub_df):
    """To make sure EvaluatorEH df_apply works as intended"""
    
    evaluator = EvaluatorEH(hub_problem,hub)
    result = evaluator.df_apply(energyhub_df)

    assert np.isclose(result.iat[0,0], 1256.12) and np.isclose(result.iat[0,1], 53.2299) and np.isclose(result.iat[1,0], 1527.39) and np.isclose(result.iat[1,1], 33.7551) , f'Unexpected result for EvaluatorEH, {result}'
    #change this to 0 to see stdout and stderr
    assert 1

def test_evaluatorEH_EP(hub, hub_problem, building, problem):
    """To make sure that base EvaluatorEP output can be used in an EvaluatorEH"""
    evaluatorEP = EvaluatorEP(problem,building)
    evaluatorEH = EvaluatorEH(hub_problem,hub)
    result = evaluatorEH(evaluatorEP([0.5]))

    assert np.isclose(result[0], 2721700000.0) and np.isclose(result[1], 33.7551), f'Unexpected result for EvaluatorEH, {result}'
    #change this to 0 to see stdout and stderr
    assert 1

def test_evaluatorEH_TS(hub):
    """To make sure that EvaluatorEH can accept a time series as input"""
    timeseries = [{0: 4.0, 1: 8.0, 2: 6.0, 3: 5.0, 4: 7.0, 5: 7.0, 6: 7.0, 7: 7.0, 8: 7.0, 9: 7.0, 10: 7.0}]
    TimeSeries_parameters = [['LOADS','Elec']]
    objectives = ['total_cost','total_carbon']
    TimeSeries_problem = EHProblem(TimeSeries_parameters, objectives)
    evaluatorEH = EvaluatorEH(TimeSeries_problem, hub)
    result = evaluatorEH(timeseries)

    assert np.isclose(result[0], 1844.18) and np.isclose(result[1], 44.6054), f'Unexpected result for EvaluatorEH, {result}'
    #change this to 0 to see stdout and stderr
    assert 1

def test_evaluatorEH_TS_df(hub):
    """To make sure that EvaluatorEH's df_apply can accept a dataframe of time series as input"""
    default_timeseries = [{0: 1.0, 1: 4.0, 2: 4.0, 3: 4.0, 4: 4.0, 5: 4.0, 6: 4.0, 7: 4.0, 8: 4.0, 9: 4.0, 10: 4.0}, \
        {0: 20.0, 1: 20.0, 2: 20.0, 3: 20.0, 4: 20.0, 5: 20.0, 6: 20.0, 7: 12.0, 8: 12.0, 9: 12.0, 10: 12.0}]
    just_modified_heat = [{0: 1.0, 1: 4.0, 2: 4.0, 3: 4.0, 4: 4.0, 5: 4.0, 6: 4.0, 7: 4.0, 8: 4.0, 9: 4.0, 10: 4.0}, \
        {0: 18.0, 1: 18.0, 2: 18.0, 3: 18.0, 4: 18.0, 5: 18.0, 6: 18.0, 7: 16.0, 8: 16.0, 9: 16.0, 10: 16.0}]
    just_modified_elec = [{0: 4.0, 1: 8.0, 2: 6.0, 3: 5.0, 4: 7.0, 5: 7.0, 6: 7.0, 7: 7.0, 8: 7.0, 9: 7.0, 10: 7.0}, \
        {0: 20.0, 1: 20.0, 2: 20.0, 3: 20.0, 4: 20.0, 5: 20.0, 6: 20.0, 7: 12.0, 8: 12.0, 9: 12.0, 10: 12.0}]
    modified_timeseries = [{0: 4.0, 1: 8.0, 2: 6.0, 3: 5.0, 4: 7.0, 5: 7.0, 6: 7.0, 7: 7.0, 8: 7.0, 9: 7.0, 10: 7.0}, \
        {0: 18.0, 1: 18.0, 2: 18.0, 3: 18.0, 4: 18.0, 5: 18.0, 6: 18.0, 7: 16.0, 8: 16.0, 9: 16.0, 10: 16.0}]
    timeseries_df = pd.DataFrame(np.array([default_timeseries,just_modified_heat, just_modified_elec, modified_timeseries]),columns= ['p1','p2'])

    TSDFparameters = [['LOADS','Elec'],['LOADS','Heat']]
    TSDFobjectives = ['total_cost','total_carbon']
    TSDFproblem = EHProblem(TSDFparameters,TSDFobjectives)

    evalutorEH = EvaluatorEH(TSDFproblem, hub)
    result = evalutorEH.df_apply(timeseries_df)
    
    assert np.isclose(result.iat[0,0], 1846.19) and np.isclose(result.iat[0,1], 33.7551) \
        and np.isclose(result.iat[1,0], 1850.01) and np.isclose(result.iat[1,1], 33.7190) \
        and np.isclose(result.iat[2,0], 1844.18) and np.isclose(result.iat[2,1], 44.6054) \
        and np.isclose(result.iat[3,0], 1847.10) and np.isclose(result.iat[3,1], 44.5693), f'Unexpected result for EvaluatorEH, {result}'
    #change this to 0 to see stdout and stderr
    assert 1

def test_evaluatorEH_EP_df(hub, hub_problem, building, problem, energyplus_df):
    """To make sure that dataframe EvaluatorEP output can be used in an EvaluatorEH"""
    evaluatorEP = EvaluatorEP(problem,building)
    evaluatorEH = EvaluatorEH(hub_problem,hub)
    result = evaluatorEH.df_apply(evaluatorEP.df_apply(energyplus_df))

    assert np.isclose(result.iat[0,0], 2.721700e+09) and np.isclose(result.iat[0,1], 33.7551) and np.isclose(result.iat[1,0], 2.705480e+09) and np.isclose(result.iat[1,1], 33.7551) , f'Unexpected result for EvaluatorEH, {result}'
    #change this to 0 to see stdout and stderr
    assert 1

def test_evaluatorSR(building, problem):
    """To make sure EvaluatorSR can be initialised and works as intended"""
    def function(values):
        return ((values[0], values[0]**2), ())

    # this denotes a problem which takes 1 input, produces 2 outputs and no constraints. The placeholder parameters/objectives will be generated automatically.
    new_problem = Problem(1,2,0)

    evaluator_1 = EvaluatorSR(function, problem)
    evaluator_2 = EvaluatorSR(function, new_problem)
    result_1 = evaluator_1([4])
    result_2 = evaluator_2([4])

    assert result_1 == (4, 16), f'Unexpected result for EvaluatorSR with EPProblem, {result_1}'
    assert result_2 == (4, 16), f'Unexpected result for EvaluatorSR with custom problem, {result_2}'

    #change this to 0 to see stdout and stderr
    assert 1
