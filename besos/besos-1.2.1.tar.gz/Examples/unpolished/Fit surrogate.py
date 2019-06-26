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
from eplus_ga import eppy_funcs as ef
from eplus_ga import sampling
from eplus_ga import objectives

from eplus_ga.problem import EPProblem
from eplus_ga.evaluator import EvaluatorEP

from sklearn import linear_model
from sklearn.model_selection import train_test_split

from eplus_ga.parameters import RangeParameter, CategoryParameter, expand_plist
# -

building = ef.get_building()

# +
parameters = expand_plist(
    {'Mass NonRes Wall Insulation':
     {'Thickness': (0.01, 0.99)},
     'NonRes Fixed Assembly Window':
     {'U-Factor':(0.1,5),
      'Solar Heat Gain Coefficient':(0.01,0.99)}
    })

# parameters.append(RangeParameter.wwr())

problem = EPProblem(parameters, ['Electricity:Facility'])

# +
#Adding categorical parameters requires converting them for scikit-learn
# -

inputs = sampling.dist_sampler(sampling.lhs, problem, 10)

evaluator = EvaluatorEP(problem, building)
outputs = evaluator.df_apply(inputs)

train_in, test_in, train_out, test_out = train_test_split(inputs, outputs, test_size=0.2)

reg = linear_model.LinearRegression()
reg.fit(train_in, train_out)
results = test_in.copy()
results['energy use'] = test_out
results['predicted'] = reg.predict(test_in)
results

inputs


