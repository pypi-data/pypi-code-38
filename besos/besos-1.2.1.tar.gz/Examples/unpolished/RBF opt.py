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

from besos.optimizer import rbf_opt
from besos.evaluator import EvaluatorSR
from besos.parameters import Parameter, RangeParameter
from besos.problem import Problem

# +
def obj_funct(x):
    return (x[0]*x[1] - x[2],),()

param_list = [Parameter(value_descriptor=RangeParameter(0,10)) for _ in range(3)]

problem = Problem(param_list, 1)

evaluator = EvaluatorSR(obj_funct, problem)
# -

rbf_opt(evaluator, 30)


