import pytest

import eppy_funcs as ef
from evaluator import EvaluatorEP, EvaluatorSR
from parameters import RangeParameter, CategoryParameter, Parameter, FieldSelector, FilterSelector, GenericSelector, wwr
from problem import EPProblem, Problem
from optimizer import NSGAII
from objectives import MeterReader
import sampling


@pytest.fixture
def building():
    building = ef.get_building(mode='json')
    # we need the json example file because of how the insulation_filter function works


def test_init(building):
    """to make sure each type of selector is created as expected"""

    def insulation_filter(building):
        return [obj for name, obj in building['Material'].items() if 'Insulation' in name]

    field_selector = FieldSelector(class_name='Material', object_name='Mass NonRes Wall Insulation', field_name='Thickness')
    filter_selector = FilterSelector(insulation_filter, 'Thickness')
    generic_selector = GenericSelector(set=ef.wwr_all, setup=ef.one_window)

    #basic checks for the expected output format
    assert str(field_selector) == "FieldSelector(field_name='Thickness', class_name='Material', object_name='Mass NonRes Wall Insulation')", f'FieldSelector not properly initialised: {field_selector}'
    assert filter_selector.field_name == 'Thickness' and str(type(filter_selector.get_objects)) =="<class 'method'>", f'FilterSelector not properly initialised: {filter_selector}'
    assert str(type(generic_selector.set)) =="<class 'method'>" and str(type(generic_selector.setup)) =="<class 'method'>", f'GenericSelector not properly initialised: {generic_selector}'

    #change this to 0 to see stdout and stderr
    assert 1
