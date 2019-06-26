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

from besos.parameters import RangeParameter, expand_plist, wwr
from besos.evaluator import EvaluatorEP
from besos.problem import EPProblem
from besos import optimizer
import platypus

# +
building = ef.get_building()

parameters=expand_plist(
    {'NonRes Fixed Assembly Window':
     {'U-Factor':(0.1,5),
      'Solar Heat Gain Coefficient':(0.01,0.99)
     },
     'Mass NonRes Wall Insulation':{'Thickness':(0.01,0.09)},
    })
parameters.append(wwr())

objectives = ['Electricity:Facility', 'Gas:Facility']

problem = EPProblem(parameters, objectives)

evaluator = EvaluatorEP(problem, building)
# -

s = optimizer.NSGAII(evaluator, evaluations=10, population_size=2)
s

# +
# s = optimizer.OMOPSO(evaluator, evaluations=30, population_size=10, epsilons=4)
# s = Optimizer.EpsMOEA(evaluator, population_size=2, evaluations=6)
# s = Optimizer.GDE3(evaluator, population_size=10, evaluations=20)
# s = Optimizer.SPEA2(evaluator, population_size=10, evaluations=20)
# s = Optimizer.NSGAIII(evaluator,population_size=10, evaluations=20)
# -


