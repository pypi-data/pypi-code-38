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
from besos.evaluator import EvaluatorEP, AdaptiveSR
from besos.parameters import RangeParameter, expand_plist, wwr
from besos.problem import EPProblem

import pyKriging
from pyKriging.krige import kriging
import numpy as np

import pandas as pd

from typing import Union, List, Tuple
# -

# Adaptive Surrogate models require more setup that other parts of BESOS, since they have several optional features, and there are different approaches to using them. Below is the template that can be used to make an adaptive surrogate.

# +
tabular = Union[np.array, pd.DataFrame]
DF = pd.DataFrame

class ExampleTemplate(AdaptiveSR):
    # helper functions provided by AdaptiveSR (Generally avoid editing these, but use them as needed)
    # append_data(X, y)
    # do_infill
    # get_from_reference
    
    # functions with defaults (These can be removed from this template if you like the defaults)
        # They may depend on some of the optional functions in order to work if using the defaults
    # __init__
    # infill (depends on -> get_infill)
    # update_model
    
    # optional functions (These will not work unless you implement them)
    # get_infill
    
    # required functions
    # train
    # eval_single
    
    def __init__(self, custom_argument_1, custom_arg_2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # do stuff with custom arguments here
    
    def get_infill(self, num_datapoints: int) -> tabular:
        """Generates data that is most likely to improve the model, and can be used for retraining.

        :param num_datapoints: the number of datapoints to generate
        :return: the datapoints generated, in some tabular datastructure
        """
        raise NotImplementedError

    def update_model(self, new_data: tabular, old_data: DF = None) -> None:
        """Modifies self.model to incorporate the new data.

        This function should not edit the existing data

        :param new_data: a table of inputs and outputs
        :param old_data: the table of inputs and outputs without the new data
        :return: None
        """
        self.train()
        
    def infill(self, num_datapoints: int) -> None:
        """Adds num_datapoints samples to the model and updates it.

        :param num_datapoints: number of datapoints to add to the model's training set
        :return: None
        """
        inputs: DF = self.problem.to_df(self.get_infill(num_datapoints), 'inputs')
        outputs: DF = self.get_from_reference(inputs)
        self.do_infill(pd.concat([inputs, outputs], axis=1))

    def train(self) -> None:
        """Generates a new model using the stored data, and stores it as self.model"""
        pass

    def eval_single(self, values: List) -> Tuple:
        """Evaluates a single input point

        :param values: The datapoint to evaluate
        :param **kwargs:
        :return: A tuple of the predicted outputs for this datapoint
        """
        pass
# -

# Here we will go through piece by piece how to wrap a model from pyKrigging in our setup.

class KrigingEval(AdaptiveSR):
    # The model cannot handle multiple objectives, so we check for this when initializing
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.problem.num_outputs != 1:
            raise ValueError('This model cannont handle multiobjective problems.')
        if self.problem.num_constraints != 0:
            raise ValueError('This model cannont handle constrained problems.')
    
    # pyKriging models are able to generate datapoints which will improve the model the most
    # **kwargs is included, since the model's function has some options which we may want to access
    # such as the ability to sample near the minimum, instead of near the point of greatest uncertainty
    def get_infill(self, num_datapoints, **kwargs):
        return self.model.infill(num_datapoints, **kwargs)
    
    # since pyKriging's model has an addPoint method, we will use it to update the model instead
    # of initialising a new one each time. We loop through all of the new datapoints
    # and add them one at a time, then retrain the inner model.
    # note that self.model.train is not the same as self.train
    def update_model(self, new_data, old_data = None) -> None:
        for index, *row in new_data.itertuples():
            inputs = row[:self.problem.num_inputs]
            output = row[-1]
            assert len(row) == self.problem.num_inputs + self.problem.num_outputs
            self.model.addPoint(inputs, output)
        self.model.train()
    
    
    
    # The infill function will work automatically, since we have defined get_infill and update_model
    
    
    # we initialize and store a kriging model on the stored training data, and then
    # run the internal model's train function.
    def train(self):
        self.model = kriging(self.data.values[:,:-1], self.data.values[:,-1])
        self.model.train()
    
    # this model expects a 2d array representing a batch of inputs, but we only want 
    # to evaluate one input point at a time, so we wrap the inputs in a list before passing
    # them to the model
    def eval_single(self, values):
        return ((self.model.predict(list(values)),), ())

# +
building = ef.get_building()

parameters=expand_plist(
    {'Mass NonRes Wall Insulation':
      {'Thickness': (0.05, 0.99)}
    })

parameters.append(wwr())

problem = EPProblem(parameters)

evaluator = EvaluatorEP(problem, building)

inputs = sampling.dist_sampler(sampling.lhs, problem, 10)
inputs = sampling.add_extremes(inputs, problem)
# this helps this specific evaluator auto-detect the min/max correctly
# -

x = sampling.dist_sampler(sampling.lhs, problem, 10)
x

sampling.add_extremes(x, problem)

k = KrigingEval(reference=evaluator)

k.do_infill(inputs) # even with cached evaluator results, this will take time for the pyKriging train step

k.model.train()

k.model.plot()

k.infill(5) 

k.model.plot()

k.data


