"""
This module is used to create and run Evaluators for different models.

Evaluators allow for rapid model simulating or solving with input variable manipulation
and output variable filtering.

Currently there are four specific evaluators: EvaluatorSR(surrogate model), AdaptiveSR(adaptive sampling), EvaluatorEP(EnergyPlus), and EvaluatorEH(PyEHub).
The Evaluators wrap their respective modeling tools with the evaluator interface.
"""
import json
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
import os
import copy
from contextlib import contextmanager
from functools import lru_cache, wraps
from pathlib import Path
from typing import Callable, Tuple, List, Union
from warnings import warn
import pathos.multiprocessing as mp
import time
import platform

import pandas as pd
from pandas import DataFrame as DF
import numpy as np
import platypus

import config
from problem import Problem
from objectives import read_eso

import pyehub
import pyehub_funcs as pf
from pyehub.outputter import output_excel

import pdb
import yaml



def _list_cache(enabled=config.cache['enabled'], size=config.cache['size'],
                typed=config.cache['typed']):
    """Decorator that allows the lru_cache (last recently used cache)
    to work on functions that receive lists"""

    def _list_cache_decorator(f):
        if enabled:
            cache_f = lru_cache(size, typed)(f)

            @wraps(cache_f)
            def safe_f(individual, *args, **kwargs):
                return cache_f(tuple(individual), *args, **kwargs)

            safe_f.cache_clear = cache_f.cache_clear
            return safe_f
        # add a no-op as the cache clear operation so it does not error if disabled in the config
        f.cache_clear = lambda: None
        return f

    return _list_cache_decorator


@contextmanager
def working_directory(path=None):
    old_wd = os.getcwd()
    if path is None:
        tempdir = tempfile.TemporaryDirectory()
        path = tempdir.name
    else:
        tempdir = None
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(old_wd)
        if tempdir is not None:
            tempdir.cleanup()


def run(building, schema=config.files['data dict'], epw=config.files['epw'],
        out_dir=config.out_dir, err_dir=config.err_dir, error_mode='Silent'):
    def resolve(path):
        if path is None:
            return None
        return Path(path).resolve()

    schema, epw, out_dir, err_dir = (resolve(p) for p in (schema, epw, out_dir, err_dir))
    with working_directory(out_dir) as out_dir:
        try:
            building_path = 'in.idf'
            building.saveas(building_path)
        except AttributeError:
            building_path = str(Path(out_dir, 'in.epJSON'))
            with open(building_path, 'w') as f:
                json.dump(building, f)
        try:
            if platform.system() is 'Windows':
                subprocess.run(['energyplus', '--idd', str(schema),
                                '--weather', str(epw), building_path], check=True, shell=True)
            else:
                subprocess.run(['energyplus', '--idd', str(schema),
                                '--weather', str(epw), building_path], check=True, shell=False)
            results = read_eso(out_dir)
            return results
        except subprocess.CalledProcessError as e:
            if err_dir is not None and Path(out_dir).resolve() != Path(err_dir).resolve():
                if os.path.exists(err_dir):
                    shutil.rmtree(err_dir)
                shutil.copytree(out_dir, err_dir)
                if error_mode != 'Silent':
                    filename = str(Path(err_dir, 'eplusout.err'))
                    file = open(filename, "r")
                    for line in file:
                        print(line)
                    print()
            raise e


class AbstractEvaluator(ABC):
    """Base class for Evaluators.

    This template requires that Evaluators are callable.
    It also gives them the df_apply method and result caching."""

    error_mode_options = {'Failfast', 'Silent', 'Print'}

    def __init__(self, problem: Problem,
                 error_mode='Failfast', error_value: tuple = None, multi = False):
        """

        :param problem: description of the inputs and outputs the evaluator will use
        :param error_mode: One of {'Failfast', 'Silent', 'Print'}.
            Failfast: Any error aborts the evaluation.
            Silent: Evaluation will return the `error_value` for any lists of values that raise an error.
            Print: Same as silent, but warnings are printed to stderr for any errors.
        :param error_value: The value of the evaluation if an error occurs. Incompatible with error_mode='Failfast'.
            must have the form (objective_values, constraint_values).
        :param multi: whether or not to use multiprocessing, using this disables cache
        """
        self.problem = problem
        self.error_mode = error_mode
        self.error_value = error_value
        self.validate_error_mode()
        self.multi = multi
        # this makes the cache instance-specific instead of class-specific
        if not self.multi:
            self._call = _list_cache()(self._uncached_call)

    # TODO: Accept more flexible input formats
    # Factoring out some of the code from _call related to handling different tuple formats might be of use
    def validate_error_mode(self):
        msg = f'Invalid error mode, only {self.error_mode_options} are allowed'
        assert self.error_mode in self.error_mode_options, msg
        if self.error_mode == 'Failfast':
            assert self.error_value is None, 'error value cannot be set when in Failfast mode'
            return
        # intuit error_value if needed
        if self.error_value is None:
            self.error_value = (None, None)
        err_out, err_constraint = self.error_value
        if err_out is None:
            err_out = tuple(float('inf') if minimize else float('-inf')
                            for minimize in self.problem.minimize_outputs)
        if err_constraint is None:
            # TODO: Intuit constraint error values as well
            err_constraint = ()
        msg = 'error value must match outputs length'
        assert len(err_out) == self.problem.num_outputs, msg
        msg = 'error value must match constraints length'
        assert len(err_constraint) == self.problem.num_constraints, msg
        self.error_value = (err_out, err_constraint)
        self.error_mode = self.error_mode

    @abstractmethod
    def eval_single(self, values: list, **kwargs) -> Tuple[Tuple, Tuple]:
        """Returns the objective results for a single list of parameter values.

        :param values: A list of values to set each parameter to,
            in the same order as this evaluator's inputs
        :param kwargs: Any keyword arguments
        :return: a tuple of the objectives and constraints
        """
        pass

    def _uncached_call(self, values: list, separate_constraints=None, **kwargs) -> tuple:
        # This method is a workaround to allow lru_cache to be instance-specific and work on __call__
        if separate_constraints is None:
            separate_constraints = self.problem.num_constraints > 0
        try:
            self.validate(values)
            outputs, constraints = self.eval_single(values, **kwargs)
        except Exception as e:
            if self.error_mode != 'Silent':
                msg = ''
                if self.problem.inputs is not None:
                    msg += f'for inputs: {self.problem.names("inputs")} '
                msg += f'problematic values were: {values}'
                warn(msg)
            if self.error_mode == 'Failfast':
                raise e
            else:
                outputs, constraints = self.error_value
        if separate_constraints:
            return outputs, constraints
        return outputs + constraints

    def __call__(self, values: list, separate_constraints=None, **kwargs) -> tuple:
        """Returns the objective results for a single list of parameter values.

        :param values: A list of values to set each parameter to,
            in the same order as this evaluator's inputs
        :param separate_constraints: which output format to use:
            objectives and constraints are both tuples of the measured values
            True: (objectives, constraints)
            False: objectives + constraints
            None: Same as True if there is at least one constraint, else the same as False
        :return: a tuple of the objectives' results
        """
        # Enables validation and caching in subclasses
        # Redirects calls to evaluate a list of values to the eval_single function.
        # Override eval_single, not this method.
        # Values can be empty to allow evaluating at the current state, but this is not the default behaviour
        # If this is not supported, the validate function of a subclass should reject an empty list
        if self.multi:
            return self._uncached_call(values, separate_constraints, **kwargs)
        else:
            return self._call(values, separate_constraints, **kwargs)

    def cache_clear(self):
        """Clears any cached vales of calls to this evaluator.
        This should be called whenever the evaluator's outputs could have changed."""
        if not self.multi:
            self._call.cache_clear()

    def validate(self, values):
        """Takes a list of values and checks that they are a valid input for this evaluator."""
        if len(values) != self.problem.num_inputs:
            raise ValueError(f'Wrong number of input values.'
                             f'{len(values)} provided, {self.problem.num_inputs} expected')
        for p, value in zip(self.problem.inputs, values):
            if not p.validate(value):
                raise ValueError(f'Invalid value {value} for parameter {p}')

    def estimate_time(self, df: DF, processes: int = 4, **kwargs):
        """Prints out a very rough estimate of the amount of time a job will take to complete.
        Will underestimate smaller sample sets but becomes more accurate as they become larger.

        :param df: a DataFrame where each row represents valid input values for this Evaluator.
        :param processes: amount of cores to use (only relevent when using multiprocessing)
        """
        start = time.time()
        res = self(df.iloc[0])
        end = time.time()

        if self.multi and processes > 1:
            estimate = ((end - start) * df.shape[0] / processes)
        else:
            estimate = (end - start) * df.shape[0]
        h = np.floor(estimate / 3600)
        m = np.floor((estimate % 3600) / 60)
        s = np.floor((estimate % 3600) % 60)
        print(f"Estimated time for completion: {h} hours, {m} minutes, {s} seconds")

    def df_apply(self, df: DF, keep_input = False, processes: int = 4, **kwargs):
        """Applies this evaluator to an entire dataFrame, row by row.

        :param df: a DataFrame where each row represents valid input values for this Evaluator.
        :param keep_input: whether to include the input data in the returned DataFrame
        :param processes: amount of cores to use (only relevent when using multiprocessing)
        :return: Returns a DataFrame with one column containing the results for each objective.
        """

        def process(df):
            res = df.apply(self, axis=1, result_type='expand', separate_constraints=False, **kwargs)
            return res

        if self.multi == True and processes > 1:
            if(config.out_dir != None):
                raise ValueError("out_dir is set to something other than 'None', running in parallel will not work.")
            if df.shape[0] < processes:
                processes = df.shape[0]
            pool = mp.Pool(processes = processes)
            split = np.array_split(df, processes)
            pool_res = pool.map(process, split)
            pool.close()
            pool.join()
            results = []
            for result in pool_res:
                results.append(result)
            results = pd.concat(results)
            result = results.rename({i: name for i, name in enumerate(self.problem.names('outputs'))}, axis=1)
        else:
            result = df.apply(self, axis=1, result_type='expand', separate_constraints=False, **kwargs)
            result = result.rename({i: name for i, name in enumerate(self.problem.names('outputs'))}, axis=1)
        if keep_input:
            result = pd.concat([df, result], axis=1)
        return result

    def to_platypus(self) -> platypus.Problem:
        """Converts this evaluator (and the underlying problem) to a platypus compatible format

        :return: A platypus Problem that can optimise over this evaluator
        """
        problem = self.problem.to_platypus()
        problem.function = self
        return problem


class EvaluatorSR(AbstractEvaluator):
    """Surrogate Model Evaluator

    This evaluator is a wrapper around a surrogate model, as defined by a function.
    """
    eval_func_format = Callable[[List], Tuple[float, ...]]

    def __init__(self, evaluation_func: eval_func_format,
                 problem: Problem, error_mode='Failfast', error_value=None, multi=False):
        """
        :param evaluation_func: a function that takes as input an list of values,
                and gives as output a tuple of the objective values for that point in the solution space
        :param problem: description of the inputs and outputs the evaluator will use
        :param multi: whether or not to use multiprocessing, using this disables cache
        """

        super().__init__(problem=problem, error_mode=error_mode, error_value=error_value, multi=multi)
        self._evaluation_func = evaluation_func

    def eval_single(self, values: List) -> Tuple:
        return self._evaluation_func(values)


tabular = Union[DF, np.array]


# TODO: Add an option/subclass that automatically bundles several single variable models into a multiobjective model.
class AdaptiveSR(AbstractEvaluator, ABC):
    """A Template for making adaptive sampling based models compatible with the evaluator interface."""

    # helper functions provided by AdaptiveSR (Generally avoid editing these, but use them as needed)
    # append_data(X, y)
    # do_infill
    # get_from_reference

    # functions with defaults (These can be removed from this template if you like the defaults)
    # They may depend on some of the optional functions in order to work if using the defaults
    # __init__
    # infill -> get_infill, _update_model
    # update_model

    # optional functions (These will not work unless you implement them)
    # get_infill

    # required functions
    # train
    # eval_single

    def __init__(self, reference: AbstractEvaluator = None,
                 error_mode='Failfast', error_value=None, multi=False):
        self.reference: AbstractEvaluator = reference
        super().__init__(problem=reference.problem, error_mode=error_mode, error_value=error_value, multi=multi)

        self.model = None
        self.data: DF = pd.DataFrame(columns=self.problem.names(parts=['inputs', 'outputs', 'constraints']))

    @property
    def problem(self):
        return self.reference.problem

    @problem.setter
    def problem(self, value: Problem):
        self.reference.problem = value

    def append_data(self, data: tabular, deduplicate=True) -> None:
        """Adds the X and y data to input_data and output_data respectively

        :param data: a table of training data to store
        :param deduplicate: whether to remove duplicates from the combined DataFrame
        :return:
        """
        self.cache_clear()  # TODO: decide on a consistent way of tracking this
        # can we assume users will only modify the data using this method or will call cache_clear themselves
        new_data = self.problem.to_df(data, ['inputs', 'outputs', 'constraints'])
        self.data = self.data.append(new_data, ignore_index=True)
        if deduplicate:
            self.data.drop_duplicates(inplace=True)

    def get_infill(self, num_datapoints: int) -> tabular:
        """Generates data that is most likely to improve the model, and can be used for retraining.

        :param num_datapoints: the number of datapoints to generate
        :return: the datapoints generated, in some tabular datastructure
        """
        raise NotImplementedError

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
        if self.model is None:
            self.train()
        else:
            self.update_model(df, old_df)

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

    @abstractmethod
    def train(self) -> None:
        """Generates a new model using the stored data, and stores it as self.model"""
        pass

    @abstractmethod
    def eval_single(self, values: List, **kwargs) -> Tuple:
        """Evaluates a single input point

        :param values: The datapoint to evaluate
        :param kwargs: Arbitrary keyword arguments.
        :return: A tuple of the predicted outputs for this datapoint
        """
        pass

    def get_from_reference(self, X: tabular) -> DF:
        """Use the reference evaluator to get the real value of a dataframe of datapoints

        :param X: a table containing the datapoints to evaluate
        :return: a DataFrame containing the results of the datapoints
        """
        df = self.problem.to_df(X, 'inputs')
        return self.reference.df_apply(df)


class EvaluatorEP(AbstractEvaluator, ABC):
    """This evaluator uses a Problem to modify a building, and then simulate it.
    It keeps track of the building and the weather file."""

    def __init__(self, problem: Problem,
                 building, epw=config.files['epw'], out_dir=config.out_dir,
                 err_dir=config.err_dir, error_mode='Failfast', error_value=None, multi=False):
        """
        :param problem: a parametrization of the building and the desired outputs
        :param building: the building that is being simulated.
        :param epw: the epw file representing the weather
        :param out_dir: the directory used for files created by the EnergyPlus simulation.
        :param err_dir: the directory where files from a failed run are stored.
        :param error_mode: One of {'Failfast', 'Silent', 'Print'}.
            Failfast: Any error aborts the evaluation.
            Silent: Evaluation will return the `error_value` for any lists of values that raise an error.
            Print: Same as silent, but warnings are printed to stderr for any errors.
        :param error_value: The value of the evaluation if an error occurs. Incompatible with error_mode='Failfast'.
        :param multi: whether or not to use multiprocessing, using this disables cache

        """
        super().__init__(problem=problem, error_mode=error_mode, error_value=error_value, multi=multi)
        self.out_dir = out_dir
        self.err_dir = err_dir
        for io in self.problem:
            io.setup(building)
        self.building = building
        self.epw = epw

    def df_apply(self, df: DF, keep_input = False, processes: int = 4, **kwargs):
        """Applies this evaluator to an entire dataFrame, row by row.

        :param df: a DataFrame where each row represents valid input values for this Evaluator.
        :param keep_input: whether to include the input data in the returned DataFrame
        :param processes: amount of cores to use (only relevent when using multiprocessing)
        :return: Returns a DataFrame with one column containing the results for each objective.
        """

        # Helper function for multiprocessing
        def process(df):
            res = df.apply(self, axis=1, result_type='expand', separate_constraints=False, **kwargs)
            return res

        if self.multi == True and processes > 1:
            if(config.out_dir != None):
                raise ValueError("out_dir is set to something other than 'None', running in parallel will not work.")
            if df.shape[0] < processes:
                processes = df.shape[0]
            pool = mp.Pool(processes = processes)
            split = np.array_split(df, processes)
            pool_res = pool.map(process, split)
            pool.close()
            pool.join()
            results = []
            for result in pool_res:
                results.append(result)
            results = pd.concat(results)
            result = results.rename({i: name for i, name in enumerate(self.problem.names('outputs'))}, axis=1)
        else:
            result = df.apply(self, axis=1, result_type='expand', separate_constraints=False, **kwargs)
            result = result.rename({i: name for i, name in enumerate(self.problem.names('outputs'))}, axis=1)

        # Fixes Dataframe output when using Multiply or Add mode
        j = 0
        for parameter in self.problem.inputs:
            if not isinstance(parameter, int):
                if parameter.mode is not 'Set':
                    names = self.problem.names('inputs')
                    objects = parameter.selector.get_objects(self.building)
                    values = parameter.selector.get(self.building)
                    if parameter.mode is 'Multiply':
                        df.rename(columns={names[j] : names[j] + ' Multiplier'}, inplace=True)
                    if parameter.mode is 'Add':
                        df.rename(columns={names[j] : names[j] + ' Addend'}, inplace=True)
            j += 1
        if keep_input:
            result = pd.concat([df, result], axis=1)
        return result

    def eval_single(self, values: list):
        current_building = copy.deepcopy(self.building)
        for p, value in zip(self.problem.inputs, values):
            # apply the modification of each parameter to the building using the corresponding value
            p.transformation_function(current_building, value)
        results = run(current_building, out_dir=self.out_dir, err_dir=self.err_dir, epw=self.epw, error_mode=self.error_mode)
        outputs = tuple((objective(results) for objective in self.problem.outputs))
        constraints = tuple((constraint(results) for constraint in self.problem.constraints))
        return outputs, constraints

    @property
    def building(self):
        return self._building

    @building.setter
    def building(self, value):
        """Changes the building simulated.
        Changing this resets the cache.

        :param value: the building to use
        :return: None
        """
        self.cache_clear()
        self._building = value

    @property
    def epw(self):
        return self._epw

    @epw.setter
    def epw(self, value: str) -> None:
        """Changes the epw file used with this building.
        Changing this resets the cache.

        :param value: path to the new epw file to use.
        :return: None
        """
        self.cache_clear()
        self._epw = value


class EvaluatorEH(AbstractEvaluator, ABC):
    """This evaluator uses a Problem to modify an energy hub, and then solve it."""

    def __init__(self, problem:Problem,
                 hub, out_dir = config.out_dir,err_dir = config.err_dir,
                  error_mode='Failfast', error_value=None, multi=False):
        super().__init__(problem=problem, error_mode=error_mode, error_value=error_value, multi=multi)
        #TODO: Either fully port the evaluator over to the config.py or switch everything over to config.yaml
        self.out_dir = out_dir
        self.err_dir = err_dir
        self.hub = hub
        self.problem = problem
        with open('config.yaml', 'r') as file:
            self.config_settings = yaml.safe_load(file)
    """
        :param problem: a parametrization of the hub and the desired outputs
        :param hub: the energy hub that is being simulated.
        :param out_dir: the directory used for files created by the PyEHub simulation.
        :param err_dir: the directory where files from a failed run are stored.
        :param error_mode: One of {'Failfast', 'Silent', 'Print'}.
            Failfast: Any error aborts the evaluation.
            Silent: Evaluation will return the `error_value` for any lists of values that raise an error.
            Print: Same as silent, but warnings are printed to stderr for any errors.
        :param error_value: The value of the evaluation if an error occurs. Incompatible with error_mode='Failfast'.
        :param multi: whether or not to use multiprocessing, using this disables cache
    """

    # Need to overwrite __call__ due to default __call__ cacheing failing on time series values.
    def __call__(self, values: list, separate_constraints=None, **kwargs) -> tuple:
        # TODO: add caching that works with time series values
        return self._uncached_call(values, separate_constraints, **kwargs)

    #override of validate due to pyehub model inputs being lists
    def validate(self, values):
        if len(values) != self.problem.num_inputs:
            raise ValueError(f'Wrong number of input values.'
                             f'{len(values)} provided, {self.problem.num_inputs} expected')

    def eval_single(self, values:list) -> tuple:
        current_hub = copy.deepcopy(self.hub)
        pf.pyehub_parameter_editor(current_hub, self.problem.inputs, values)

        objectives = self.problem.names('outputs')
        current_hub.compile()
        primary_objective = objectives[0]
        current_hub.objective = primary_objective
        

        results = current_hub.solve()

        if(self.out_dir != None):
            output_file = self.config_settings['output_file']
            self.out_dir = self.out_dir/output_file
            output_excel(results['solution'], self.out_dir,
                 time_steps=len(current_hub.time), sheets=['other', 'capacity_storage', 'capacity_tech'])

        outputs = tuple((pf.get_by_path(results['solution'], [objective]) for objective in objectives))
        constraints = tuple()

        return outputs, constraints


