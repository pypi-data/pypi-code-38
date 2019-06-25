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
from besos import optimizer
from besos import sampling
from besos.evaluator import EvaluatorEP, EvaluatorSR
from besos.parameters import RangeParameter, expand_plist, wwr
from besos.problem import EPProblem

import pandas as pd
import numpy as np

from sklearn import linear_model
from sklearn.model_selection import train_test_split

import random
# -

idf = ef.get_idf()

# +
parameters = expand_plist(
    #{'Name of object in idf':
    # {'Property Name':(min, max)}}
    {'NonRes Fixed Assembly Window':
     {'UFactor':(0.1,5),
      'Solar Heat Gain Coefficient':(0.01,0.99)
     },
     'Mass NonRes Wall Insulation':{'Thickness':(0.01,0.09)},
    })
parameters.append(wwr())

problem = EPProblem(parameters)
evaluator = EvaluatorEP(problem, idf)

# +
sampler = sampling.lhs
numSamples = 5

inputs = sampling.dist_sampler(sampling.lhs, problem, numSamples)

outputs = evaluator.df_apply(inputs)
# -

train_in, test_in, train_out, test_out = train_test_split(inputs, outputs, test_size=0.2)

reg = linear_model.LinearRegression()
reg.fit(train_in, train_out)
#r2 score

# +
def evaluation_func(ind):
    return ((reg.predict([ind])[0][0],),())

surrogate = EvaluatorSR(evaluation_func, problem)
# -

surrogate.df_apply(test_in, keep_input=True)

predictions = test_in.copy()
predictions['prediction'] = surrogate.df_apply(predictions)#reg.predict(test_in)
predictions['answer'] = test_out
predictions

s = optimizer.NSGAII(surrogate, 1000)

s


