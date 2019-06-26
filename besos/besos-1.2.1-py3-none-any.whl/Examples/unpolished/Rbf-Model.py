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

# This notebook implements a rbf adaptive surrogate. It could be used as the model half of an rbf-opt algorithm, but would need a sample selection algorithm as well.

# +
from besos import eppy_funcs as ef
from besos import sampling
from besos.evaluator import EvaluatorEP, AdaptiveSR, EvaluatorSR
from besos.parameters import RangeParameter, expand_plist, wwr
from besos.problem import EPProblem

import numpy as np
import pandas as pd
import scipy.interpolate

# +
from typing import Union, List, Tuple

tabular = Union[np.array, pd.DataFrame]
DF = pd.DataFrame

class RBF(AdaptiveSR):
    def __init__(self, *args, **kwargs):
        self.model_kwargs = {}
        for name in ['function', 'epsilon', 'smooth', 'norm']:
            if name in kwargs:
                self.model_kwargs[name] = kwargs.pop(name)
        super().__init__(*args, **kwargs)
        self.obj_models = None
        self.constr_models = None

    def train(self) -> None:
        """Generates a new model using the stored data, and stores it as self.model"""
        inputs = (self.data[self.problem.names('inputs')].values[:,i] for i in range(problem.num_inputs))
        outputs = self.data[self.problem.names('outputs')].values
        constraints = self.data[self.problem.names('outputs')].values
        def train_single(output):
            return scipy.interpolate.Rbf(*inputs, output, **self.model_kwargs)
    
        self.obj_models = [train_single(outputs[:,i]) for i in range(self.problem.num_outputs)]
        self.constr_models = [train_single(outputs[:,i]) for i in range(self.problem.num_constraints)]

    def eval_single(self, values: List) -> Tuple:
        values = ([v] for v in values)
        objectives = tuple(model(*values)[0] for model in self.obj_models)
        constraints = tuple(model(*values)[0] for model in self.constr_models)
        return (objectives, constraints)
    
    def do_infill(self, data: DF) -> None:
        """Updates the model using the inputs X and outputs y, and stores the added data

        :param data: a table of training data
        :return: None
        """
        old_df = self.data
        df, parts = self.problem.partial_df(data, parts=['inputs', 'outputs', 'constraints'])
        if parts == ['inputs']:
            outputs: DF = self.get_from_reference(df)
            df = pd.concat([df, outputs], axis=1)
        self.append_data(df)
        self.train()

# +
building = ef.get_building()

parameters=expand_plist(
    {'Mass NonRes Wall Insulation':
      {'Thickness': (0.01, 0.99)},
     'NonRes Fixed Assembly Window':
     {'U-Factor':(0.1,5),
      'Solar Heat Gain Coefficient':(0.01,0.99)}
    })

parameters.append(wwr())

problem = EPProblem(parameters)

# a fast function for debugging
def placeholder(values):
    return (sum(values),),()

evaluator = EvaluatorEP(problem, building)
#evaluator = EvaluatorSR(placeholder, problem)

inputs = sampling.dist_sampler(sampling.lhs, problem, 10)
# -

k = RBF(reference=evaluator)

k.do_infill(inputs)

k.df_apply(inputs, keep_input=True)


