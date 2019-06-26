# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 0.8.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Two types of outputs are supported: Objectives and Constraints. These are both made using the `MeterReader` and `VariableReader` classes. The only difference is how they are used by the problem.

# +
from besos import eppy_funcs as ef
from besos import sampling
from besos.evaluator import EvaluatorEP
from besos.parameters import RangeParameter, wwr, FieldSelector, Parameter
from besos.objectives import MeterReader, VariableReader, clear_outputs
from besos.problem import EPProblem, Problem
from besos.optimizer import NSGAII

import pandas as pd
# -

building = ef.get_building()
clear_outputs(building)

# Objectives and constraints can be specified in one of 3 ways. The most direct is by calling their constructor.

objectives = [MeterReader(key_name='Electricity:Facility', class_name='Output:Meter', frequency='Hourly')]
EPProblem(outputs=objectives)

# The constructor has defaults, so we can often ommit `class_name` and `frequency`. Since the key name is often all that is needed, we can just use a list of the `key_names`. This list will be automatically be converted by `EPProblem`. Meters and variables that do not have a `frequency` specified will default to any frequency that is already used for that output, or if none is used yet then they will use Hourly.

objectives = ['Electricity:Facility']
EPProblem(outputs=objectives)

# If we do not need the output-reading features of meters, we can use `Problem` instead of `EPProblem`, and they will be converted to `Objective` objects which act as placeholders. `EPProblem` converts them to `Meter:Reader` objects. Either of these conversions can be overriden using the converters argument.  

objectives = ['any', 'names', 'work']
Problem(outputs=objectives)

# The `func` argument to objectives/constraints is used to aggrgate the individual measurements from the model. By default, all measurements are added together. If we wanted to instead minimize the variance, we would need to write our own aggrgation function

# +
def variance(result):
    return result.data['Value'].var()

objectives = [MeterReader('Electricity:Facility', name='Electricity Usage'),
              MeterReader('Electricity:Facility',func=variance, name='Electricity Variance')
             ]
# -

# When we want to specify the direction of optimisation, we can use `minmize_outputs`. The default is true for all objectives. Here we say we want to search for a design that has low but highly variable electricity use, and no more than 800 kg of CO2 emission. (The electricity use objectives were defined in the cell above)

# +
inputs = [wwr(), Parameter(FieldSelector(class_name='Material',
                                         object_name='Mass NonRes Wall Insulation',
                                         field_name='Thickness'),
                           RangeParameter(0.01, 0.99))
         ]

evaluator = EvaluatorEP(EPProblem(inputs=inputs,
                                  outputs=objectives, minimize_outputs=[True, False],
                                  constraints=['CO2:Facility'], constraint_bounds=['<=800']),
                        building, out_dir='../E_Plus_Files/')
# -

# this cell runs the optimisation, and may take a while.
NSGAII(evaluator, evaluations=100, population_size=20)


