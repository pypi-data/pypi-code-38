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

# +
from besos import eppy_funcs as ef
from besos import sampling
from besos.evaluator import EvaluatorEP, EvaluatorSR
from besos.parameters import RangeParameter, CategoryParameter, Parameter, FieldSelector
from besos.problem import EPProblem

import pandas as pd
import copy
from subprocess import CalledProcessError
# -

# Sometimes there are parts of the design space that we want to explore that will cause the EnergyPlus simulation to fail, such as invalid combinations of parameter values. In  this example, we will sometimes try to use an undefined material `Invalid Material` in our building to represent an invalid state.

# +
building = ef.get_building()

problem = EPProblem([
    Parameter(
        FieldSelector(object_name='Mass NonRes Wall Insulation', field_name='Thickness'),
        RangeParameter(min_val = 0.01, max_val=0.99)),
    Parameter(
        FieldSelector(class_name='Construction', object_name='ext-slab', field_name='Outside Layer'),
        CategoryParameter(options=('HW CONCRETE', 'Invalid Material')))])
# -

samples = sampling.dist_sampler(sampling.lhs, problem, 5)
samples

# By default, evaluation of a DataFrame of parameters will end when an invalid combination is encountered.

try:
    EvaluatorEP(problem, building, error_mode='Failfast').df_apply(samples)
except Exception as e:
    print('caught', e)

# However sometimes we want to have a fallback value for these invalid states. This can be specified with the `error_value` argument for evaluators.  
# It must be of the form `(objective_values, constraint_values)` where objective_values and constraint_values are tuples of the same length as the number of objectives/constraints.  
#
# Since we have 1 objective and no constraints, we use a tuple with one item for objective_values, and an empty tuple for the constraint values.

# +
error_value=((10.0**20,), ())

EvaluatorEP(problem, building, error_mode='Print', error_value=error_value).df_apply(samples)
# -

# This time, the we got a warning for the invalid states, and our error value was used as their result.
#
# If we do not want to display these warnings, we can set the `error_mode='Silent'`  
#
# Ommiting the error value will use a reasonable default, set to the opposite of what we are optimizing each objective towards. (This does not work for problems with constraints)

evaluator = EvaluatorEP(problem, building, error_mode='Silent')
print('Error value defaulted to:', evaluator.error_value)

evaluator.df_apply(samples)


