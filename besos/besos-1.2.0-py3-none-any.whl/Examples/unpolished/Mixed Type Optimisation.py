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

from besos.parameters import CategoryParameter, RangeParameter, Parameter
from besos.evaluator import EvaluatorSR
from besos.problem import Problem
from besos import optimizer
from platypus.config import PlatypusConfig

# Optimizing a building usually requires many evaluations of that building at different parameters. 
# Therefore this example will optimize over a surrogate evaluator wrapping a quick function 
# to speed things up.  
# By default, platypus does not support using categories and ranges in the same problem. The wrapped algorithms  
# available in the optimizer package *do* support mixed type optimization.

# +
parameters=[Parameter(value_descriptor=CategoryParameter(list(range(80,90))), name='1st'),
            Parameter(value_descriptor=CategoryParameter(list(range(80,90))), name='2nd'),
            Parameter(value_descriptor=RangeParameter(3, 100), name='3rd')
           ]

def mixed_types(vals):
    vals = list(vals)
    num = vals.pop(-1)
    objectives = tuple(num % v for v in vals)
    return (objectives,())


evaluator = EvaluatorSR(mixed_types, Problem(parameters, 2))
# -

# by default variator='automatic' i.e. it will be constructed based on the evaluator used
optimizer.EpsMOEA(evaluator, epsilons=10)

# If you are customizing more of your optimization, you can acces the mixed type operator for your evauluator
# using the function `optimizer.get_operator` (Use mutation=True if you want a mutator instead of a variator)

# +
variator = optimizer.get_operator(evaluator.to_platypus())

result = optimizer.EpsMOEA(evaluator, variator=variator, epsilons=10)
result
# -


