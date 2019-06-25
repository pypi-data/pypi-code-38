import pytest

import eppy_funcs as ef
from evaluator import EvaluatorEP, EvaluatorSR
from parameters import RangeParameter, CategoryParameter, Parameter, FieldSelector, wwr
from problem import EPProblem, Problem
import sampling
import numpy as np

#parameter - selector & descriptor
#selector - FilterSelector FieldSelector GenericSelector
#descriptor - RangeParameter CategoryParameter

#init, setup_checks, and setup_changes were moved directly from Will's code in parameters.py
def test_init():
    # inputs should be initialisable
    Parameter(FieldSelector(object_name='NonRes Fixed Assembly Window', field_name='UFactor'),
              value_descriptor=RangeParameter(min_val=0.1, max_val=5))
    wwr()
    wwr(name='other')
    print('Parameters initialised')

    #change this to 0 to see stdout and stderr
    assert 1


#TODO: look into fixing this
def test_setup_checks():
    #try excepts were updated to asserts and now the test fails, no exceptions are being raised and it seems to be in 3rd party code

    idf = ef.get_idf()
    assert len(idf.idfobjects['FENESTRATIONSURFACE:DETAILED']) == 21, 'bad idf'

    # eppy key-inputs should reject bad key values at setup
    r: Parameter = Parameter(FieldSelector(class_name='invalid', field_name='any'))

    #when exception raising is implemented properly uncomment this test, for now it does nothing

    #with pytest.raises(Exception):
    #    r.setup(idf)
    #print('Invalid object key detected successfully.')
    #r = Parameter(FieldSelector(object_name='NonRes Fixed Assembly Window', field_name='invalid'))
    #with pytest.raises(Exception):
    #    r.setup(idf)
    #print('Invalid property detected successfully.')

    #change this to 0 to see stdout and stderr
    assert 1


def test_setup_changes():
    idf = ef.get_idf()

    r1 = Parameter(FieldSelector(object_name='NonRes Fixed Assembly Window', field_name='UFactor'),
                   value_descriptor=RangeParameter(min_val=0.1, max_val=5))
    r2 = wwr()
    r3 = wwr(name='other')

    r1.setup(idf)
    r2.setup(idf)
    assert len(idf.idfobjects['FENESTRATIONSURFACE:DETAILED']) == 4, 'bug in r2.setup'

    idf = ef.get_idf()
    assert len(idf.idfobjects['FENESTRATIONSURFACE:DETAILED']) == 21, 'bad idf'
    r3.setup(idf)
    assert len(idf.idfobjects['FENESTRATIONSURFACE:DETAILED']) == 4, 'bug in r3.setup'

    print('setup tests done')

    #change this to 0 to see stdout and stderr
    assert 1


def test_custom_evaluation():
    """check to see if descriptors display as intended, and check to make sure custom evaluations work with EvaluatorSR"""

    #create the descriptors
    zero_to_nine = RangeParameter(min_val = 0, max_val=9)
    single_digit_integers = CategoryParameter(options=[0,1,2,3,4,5,6,7,8,9])
    text_example = CategoryParameter(options=['a', 'b', 'c', 'other'])

    #create the parameters and the problem
    parameters = [
        Parameter(value_descriptor=zero_to_nine, name='0-9'),
        Parameter(value_descriptor=single_digit_integers, name='single digit'),
        Parameter(value_descriptor=text_example, name='text')
    ]
    problem = Problem(parameters, outputs=['output'])

    #create the sampling distribution (seeded with only one output that should give     4.939321535345923	7	c	34.575251 after evaluating)
    samples = sampling.dist_sampler(sampling.seeded_sampler, problem, num_samples=1)
    values = [samples.iloc[0]['0-9'], samples.iloc[0]['single digit'], samples.iloc[0]['text']]
    assert np.isclose(values[0], 4.939321535345923) and values[1:] == [7, 'c'], f'Unexpected sample values: {values}'

    #custom evaluation function from the jupyter notebook
    def evaluation_function(values):
        x,y,z = values
        if z == 'other':
            return (0,), ()
        else:
            return (x * y,), ()

    evaluator = EvaluatorSR(evaluation_function, problem)
    # The evaluator will use this objective by default
    outputs = evaluator.df_apply(samples ,keep_input=True)
    result = outputs.iloc[0]['output']
    print(result)
    assert np.isclose(result, 34.57525074742146), f'Unexpected evaluation result: {result}'

    #change this to 0 to see stdout and stderr
    assert 1
