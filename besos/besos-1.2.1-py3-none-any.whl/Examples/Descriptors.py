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

# # Descriptors

# +
from besos.parameters import RangeParameter, CategoryParameter, Parameter
from besos.problem import Problem
from besos import sampling
from besos.evaluator import EvaluatorSR 


import pandas as pd
# -

# Descriptors specify what kinds of values are valid for a parameter. Currently, two variants exist: `RangeParameter` and `CategoryParameter`.  
#
# RangeParameters have a minimum and a maximum, and allow any value in that range. The endpoints are included in the allowable range.

zero_to_nine = RangeParameter(min_val = 0, max_val=9)

# CategoryParameters have a list of options, and can only be set to the value of items from that list.

single_digit_integers = CategoryParameter(options=[0,1,2,3,4,5,6,7,8,9])
text_example = CategoryParameter(options=['a', 'b', 'c', 'other'])

# ### Sampling
# Parameters only need the Descriptor part for sampling.

# +
parameters = [
    Parameter(value_descriptor=zero_to_nine, name='0-9'),
    Parameter(value_descriptor=single_digit_integers, name='single digit'),
    Parameter(value_descriptor=text_example, name='text')
]
problem = Problem(parameters, outputs=['output'])

samples = sampling.dist_sampler(sampling.lhs, problem, num_samples=10)
samples
# -

# ### Evaluation
# Since we did not specify selectors for the parameters, we cannot evaluate them using an energy plus simulation.  
# Instead, we will use a custom evaluation function.

# +
def evaluation_function(values):
    x,y,z = values
    if z == 'other':
        return (0,), ()
    else:
        return (x * y,), ()


evaluator = EvaluatorSR(evaluation_function, problem)
# The evaluator will use this objective by default
outputs = evaluator.df_apply(samples ,keep_input=True)
# outputs is a pandas dataframe with one column since only one objective was requested
# -

outputs


