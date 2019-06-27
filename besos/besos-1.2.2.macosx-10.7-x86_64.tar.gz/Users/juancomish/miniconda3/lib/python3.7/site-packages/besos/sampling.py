import pyDOE2
import numpy as np
import pandas as pd

from typing import Callable, Any

from IO_Objects import Descriptor
from problem import Problem


_sampler = Callable[[int, int, Any], np.ndarray]  # the format of all sampler functions


def dist_sampler(sampler: _sampler, problem: Problem, num_samples: int, *args, **kwargs) -> pd.DataFrame:
    """uses the sampling function provided to generate `num_samples` sets of values
    These values will be valid for the corresponding inputs

    :param problem: Problem that the inputs should apply to
    :param sampler: a function that is used to produce the distribution of samples
    :param num_samples: number of samples to take

    :param args: Arguments passed to the sampling function
    :param kwargs: Arguments passed to the sampling function
    :return: pandas DataFrame with one column per parameter, and `num_samples` rows

    """
    samples = sampler(num_samples, problem.num_inputs, *args, **kwargs)
    data = {name: _sample_param(param, samples[:, i]) for i, (name, param)
            in enumerate(zip(problem.names('inputs'), problem.inputs))}
    df = pd.DataFrame(data)
    # enforce the correct order in case it was lost by the dictionary
    df = df[problem.names('inputs')]
    return df


def add_extremes(df, problem):
    """adds two datapoints with the minimum and maximum values for each attribute

    :param data:
    :param problem:
    :return:
    """
    new = dist_sampler(extremes, problem, 2)
    return pd.concat([df, new], ignore_index=True)


def extremes(samples: int, attributes: int=None) -> np.ndarray:
    if attributes is None:
        samples, attributes = 2, samples
    assert samples == 2, "extremes can only produce two samples"
    return np.array([np.zeros(attributes), np.ones(attributes)])


def _sample_param(parameter: Descriptor, values):
    try:
        # this will only work if p.sample is numpy compatible
        return parameter.sample(values)
    except TypeError:
        # apply non-vectorised version of p.sample
        return [parameter.sample(x) for x in values]


# all of the following return a 2d array of shape (samples, attributes)
# which contains values between 0 and 1


random: _sampler = np.random.rand


def seeded_sampler(samples: int, attributes: int, seed=0) -> np.ndarray:
    np.random.seed(seed)
    return np.random.rand(samples, attributes)


def lhs(samples: int, attributes: int, *args, **kwargs) -> np.ndarray:
    return pyDOE2.lhs(attributes, samples, *args, **kwargs)

def full_factorial(samples: int, attributes: int, level: int=None) ->np.ndarray:
   if level == None:
       level = np.int(np.exp(np.log(samples)/attributes))
       if (level**attributes) > level:
        print(f'Total number of samples ({level**attributes}) is smaller  than input ({samples}) '
              f'to have an even number of factor levels ({level}) for all parameters.')
   return pyDOE2.fullfact((np.ones([attributes]) * level).astype(int))/level
