# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import numpy as np
import numpy.ma as ma
import sklearn.model_selection
import sklearn.exceptions
import copy
import math
import random
import warnings


from sympathy.api import node
from sympathy.api.nodeconfig import Port
from sympathy.api.nodeconfig import Ports
from sympathy.api.nodeconfig import Tag
from sympathy.api.nodeconfig import Tags
from sympathy.api.exceptions import SyNodeError
from sympathy.api.exceptions import SyDataError
from sympathy.api.exceptions import sywarn
from sympathy.types.sylist import sylistReadThrough

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract

from sylib.machinelearning.descriptors import NumericType
from sylib.machinelearning.utility import table_to_array


class ParameterSearch_SuperNode(node.Node):
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    tags = Tags(Tag.MachineLearning.HyperParameters)

    inputs = Ports([
        ModelPort('in-model', name='in-model'),
        Port.Tables('param-space', name='parameter space'),
        Port.Table('X', name='X'),
        Port.Table('Y', name='Y'),
        Port.Custom('[(table,table)]', 'cross-validation',
                    name='cross-validation', n=(0, 1)),
    ])
    outputs = Ports([
        Port.Table('results', name='results'),
        Port.Table('parameters', name='parameters'),
        ModelPort('out-model', name='out-model'),
    ])
    parameters = node.parameters()
    parameters.set_integer(
        'cv', value=3, label='Cross validation splits',
        description=(
            'Number of fold in the default K-Fold cross validation. '
            'Ignored when cross-validation port is given'))

    def setup(self, node_context):
        """Utility function for loading data, model and parameters"""
        X_tbl = node_context.input['X']
        Y_tbl = node_context.input['Y']
        in_model = node_context.input['in-model']

        X = table_to_array(X_tbl)
        Y = table_to_array(Y_tbl)
        in_model.load()
        model = in_model.get_skl()

        out_model = node_context.output['out-model']
        out_model.source(in_model)
        out_model.load()
        desc = out_model.get_desc()
        desc.set_x_names(X_tbl.column_names())
        desc.set_y_names(Y_tbl.column_names())
        out_model.save()

        params = self.param_dict(desc, node_context)

        if len(node_context.input.group('cross-validation')) > 0:
            cv = [(tpl[0].get_column_to_array(tpl[0].column_names()[0]),
                   tpl[1].get_column_to_array(tpl[1].column_names()[0]))
                  for tpl in node_context.input.group('cross-validation')[0]]
        else:
            cv = None

        return X, Y, model, desc, params, cv

    def param_dict(self, desc, node_context):
        """List of parameter definitions"""
        par_tables = node_context.input['parameter space']
        if not isinstance(par_tables, sylistReadThrough):
            par_tables = [par_tables]

        pdicts = []
        for tbl in par_tables:
            pdict = {}
            for name in tbl.column_names():
                if name not in desc.types:
                    raise SyDataError('Invalid parameter {} for model {}.'
                                      .format(name, desc.name))
                col = tbl.get_column_to_array(name)
                values = list(filter(
                    lambda v: v is not ma.masked,
                    list(col)))
                values = [desc.types[name].from_string(str(val))
                          for val in values]
                pdict[name] = values
            pdicts.append(pdict)
        return pdicts

    def gen_results(self, node_context, search):
        meta_tbl = node_context.output['results']
        par_tbl = node_context.output['parameters']

        for key in sorted(search.cv_results_.keys()):
            if key != 'params':
                # sklearn sometimes give references to strings as np.arrays,
                # coerce back to normal np.arrays
                if isinstance(search.cv_results_[key], ma.core.MaskedArray):
                    col = ma.array(list(search.cv_results_[key].data),
                                   mask=search.cv_results_[key].mask)
                else:
                    col = np.array(list(search.cv_results_[key]))
                # Finally, if array contains references to objects, cast to
                # strings as last resort
                if col.dtype == np.dtype('O'):
                    col = np.array([str(o) for o in col])
                if len(col.shape) > 1:
                    col = col[:, 0]
                meta_tbl.set_column_from_array(key, col)
        params = search.cv_results_['params']
        all_keys, all_cols, all_masks = self.concatenate_parameters(params)
        for key, col, mask in zip(all_keys, all_cols, all_masks):
            par_tbl.set_column_from_array(key, ma.array(col, mask=mask))

        out_model = node_context.output['out-model']
        out_model.set_skl(search.best_estimator_)
        out_model.save()

    def concatenate_parameters(self, params):
        all_keys = set([])
        for d in params:
            all_keys = all_keys.union(set(d.keys()))
        all_keys = sorted(list(all_keys))
        all_cols = []
        all_masks = []
        for key in all_keys:
            cols = []
            masks = []
            for d in params:
                if key not in d:
                    cols.append('')
                    masks.append(1)
                else:
                    cols.append(str(d[key]))
                    masks.append(0)
            all_cols.append(cols)
            all_masks.append(masks)
        return all_keys, all_cols, all_masks


class ParameterSearch_Randomized(ParameterSearch_SuperNode):
    name = 'Randomized Parameter Search'
    icon = 'random_hyperparam.svg'
    description = (
        'Performs a randomized parameter search returning scores '
        'and best model found. Uses table as '
        'a "hypercube" of parameters to sample from. Ie. all combinations '
        'of parameters from all columns have equal chance of beeing sampled. '
        'Use masked values for parameter/columns with different lengths. ')
    nodeid = 'org.sysess.sympathy.machinelearning.randomized_parsearch'

    inputs = Ports([
        ModelPort('in-model', name='in-model'),
        Port.Table('param-space', name='parameter space'),
        Port.Table('X', name='X'),
        Port.Table('Y', name='Y'),
        Port.Custom('[(table,table)]', 'cross-validation',
                    name='cross-validation', n=(0, 1)),
    ])

    parameters = copy.deepcopy(ParameterSearch_SuperNode.parameters)
    parameters.set_integer(
        'n_iter', value=10, label='iterations',
        description='Number of randomized searches done')
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters,
        inputs,
        ParameterSearch_SuperNode.outputs)

    def execute(self, node_context):
        X, Y, model, desc, params, cv = self.setup(node_context)
        if len(params) > 1:
            sywarn('Randomized parameter search uses only'
                   'first hypercube of given parameters')

        if cv is None:
            cv = node_context.parameters['cv'].value
            n_cv = cv
        else:
            n_cv = len(cv)

        n_iter = node_context.parameters['n_iter'].value
        self.progress_i = 0

        def score_and_progress(estimator, X, y):
            self.progress_i += 1
            self.set_progress((100.0 * self.progress_i) / (n_iter * n_cv * 2))
            return estimator.score(X, y)

        search = sklearn.model_selection.RandomizedSearchCV(
            model, params[0],
            cv=cv,
            n_iter=n_iter,
            scoring=score_and_progress,
            return_train_score=True,
        )
        if len(Y.shape) > 1:
            Y = Y[:, 0].ravel()

        with warnings.catch_warnings():
            warnings.simplefilter(
                'ignore', sklearn.exceptions.ConvergenceWarning)
            search.fit(X, Y)
        self.gen_results(node_context, search)


class ParameterSearch_Grid(ParameterSearch_SuperNode):
    name = 'Grid Parameter Search'
    icon = 'hyperparam.svg'
    description = (
        'Evaluates each parameter combination in the set of parameter '
        'hypercubes given by each table in the list of parameter tables. '
        'Each parameter table specify a hypercube of dimension N where N is '
        'the number of columns in the table. Every combination of paramater '
        'values in each such cube will be sampled.')
    nodeid = 'org.sysess.sympathy.machinelearning.grid_parsearch'

    __doc__ = SyML_abstract.generate_docstring2(
        description, [],
        ParameterSearch_SuperNode.inputs,
        ParameterSearch_SuperNode.outputs)

    def count_cases(self, params, cv):
        cases = 0
        for hypercube in params:
            cases += np.prod(np.array(
                [len(pars) for pars in hypercube.values()]))
        if isinstance(cv, list):
            cases *= len(cv)
        else:
            cases *= cv
        cases *= 2
        return cases

    def execute(self, node_context):
        X, Y, model, desc, params, cv = self.setup(node_context)
        if cv is None:
            cv = node_context.parameters['cv'].value

        cases = self.count_cases(params, cv)
        self.progress_i = 0

        def score_and_progress(estimator, X, y):
            self.progress_i += 1
            self.set_progress((100.0 * self.progress_i) / cases)
            return estimator.score(X, y)

        Y = Y[:, 0]
        search = sklearn.model_selection.GridSearchCV(
            model, params,
            cv=cv,
            scoring=score_and_progress,
            return_train_score=True
        )
        with warnings.catch_warnings():
            warnings.simplefilter(
                'ignore', sklearn.exceptions.ConvergenceWarning)
            search.fit(X, Y)
        self.gen_results(node_context, search)


class _SimAnnealing_Results(object):
    def __init__(self, types, model, params, temperature, scores):
        self.types = types
        self.best_estimator_ = copy.deepcopy(model)
        self.cv_results_ = {
            'params': []
        }
        self.cv_results_['temperature'] = [temperature]
        self.cv_results_['mean_test_scores'] = [np.mean(scores)]
        self.cv_results_['best_test_scores'] = [np.mean(scores)]
        self.cv_results_['state_change'] = [True]
        self.cv_results_['std_test_scores'] = [np.std(scores)]
        for i, score in enumerate(scores):
            self.cv_results_[
                'split{}_test_score'.format(i)] = [score]
        self.cv_results_['params'] = [params]
        for name, value in params.items():
            self.cv_results_[name] = [value]

    def update(self, params, temperature, scores):
        self.cv_results_['params'].append(params)
        self.cv_results_['temperature'].append(temperature)
        self.cv_results_['mean_test_scores'].append(np.mean(scores))
        self.cv_results_['std_test_scores'].append(np.std(scores))
        for i, score in enumerate(scores):
            self.cv_results_[
                'split{}_test_score'.format(i)].append(score)
        for name, value in params.items():
            self.cv_results_[name].append(value)

    def update_best(self, params, best_score, changed):
        self.cv_results_['best_test_scores'].append(best_score)
        self.cv_results_['state_change'].append(changed)

        # for name, value in params.items():
        #     self.cv_results_['best_{}'.format(name)].append(value)

    def cast_to_arrays(self):
        for key, value in self.cv_results_.items():
            if key == 'params':
                continue
            elif (key in self.types.keys()
                  and not isinstance(self.types[key], NumericType)):
                strs = [self.types[key].to_string(val)
                        for val in self.cv_results_[key]]
                self.cv_results_[key] = np.array(strs)
            else:
                self.cv_results_[key] = np.array(self.cv_results_[key])

        rank = np.zeros(len(self.cv_results_['mean_test_scores']), dtype=int)
        sortpos = np.argsort(self.cv_results_['mean_test_scores'])
        rank[sortpos] = len(rank) - np.arange(len(rank))

        self.cv_results_['rank'] = rank


class ParameterSearch_SimulatedAnnealing(ParameterSearch_SuperNode):
    name = 'Simulated Annealing Parameter Search'
    icon = 'annealing_hyperparam.svg'
    description = (
        'Uses simulated annealing to find the optimal parameters by '
        'considering a hyper cube of all possible indices to the given '
        'parameter table. Each column of the parameter table corresponds to '
        'one axis of this cube with a range corresponding to the non-masked '
        'rows of the parameter table. '
        'The radius for the annealing process assumes that all axes have unit '
        'length regardless of the number of non-masked rows. '
        'This node should be considered _experimental_ and may change in '
        'the future')
    nodeid = 'org.sysess.sympathy.machinelearning.sim_anneal_parsearch'

    inputs = Ports([
        ModelPort('in-model', name='in-model'),
        Port.Table('param-space', name='parameter space'),
        Port.Table('X', name='X'),
        Port.Table('Y', name='Y'),
        Port.Custom('[(table,table)]', 'cross-validation',
                    name='cross-validation', n=(0, 1)),
    ])

    parameters = copy.deepcopy(ParameterSearch_SuperNode.parameters)
    parameters.set_integer(
        'n_iter', value=50, label='iterations',
        description='Number of randomized searches done')
    parameters.set_string(
        'cooling', value='Exponential', label='Cooling method',
        description='Method for lowering temperature',
        editor=node.Util.combo_editor(
            options=['Exponential', 'Linear', 'Logarithmic']))
    parameters.set_float(
        'cooling_arg', value=0.9, label='Cooling argument',
        description=(
            'Argument A to cooling method. '
            'Exponential: T=A^t   '
            'Linear ignores A   '
            'Logarithmic: T=A/log(1+t)'))
    # parameters.set_boolean(
    #     'decradius', value=False, label='Decreasing radius',
    #     description='Reduces the search radius as temperature drops')

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters,
        inputs,
        ParameterSearch_SuperNode.outputs)

    def execute(self, node_context):
        cooling = node_context.parameters['cooling'].value
        coolarg = node_context.parameters['cooling_arg'].value
        # Temporarily disabled due to unclear references to methods viability
        # decradius = node_context.parameters['decradius'].value
        decradius = False
        param_table = node_context.input['parameter space']

        X, Y, model, desc, _, cv = self.setup(node_context)
        params = [ma.compressed(param_table.get_column_to_array(name))
                  for name in param_table.column_names()]
        param_names = param_table.column_names()
        param_types = {name: desc.parameters[name]['type']
                       for name in param_names}
        n_params = np.array([len(arr) for arr in params])

        if cv is None:
            cv = node_context.parameters['cv'].value
            n_cv = cv
        else:
            n_cv = len(cv)
        n_iter = node_context.parameters['n_iter'].value

        def param_dict(indices):
            return {name:
                    param_types[name].from_string(
                        params[i][indices[i]])
                    for i, name in enumerate(param_names)}

        def eval_model(step):
            self.progress_i = 0

            def score_and_progress(estimator, X, y):
                self.progress_i += 1
                self.set_progress(step*100.0/n_iter +
                                  self.progress_i*100.0 / (n_iter*n_cv*2))
                return estimator.score(X, y)

            return sklearn.model_selection.cross_val_score(
                model, X, Y, cv=cv, scoring=score_and_progress)

        self.set_progress(0.0)
        best_par = (np.random.random(len(params)) * n_params).astype(int)
        dct = param_dict(best_par)
        model.set_params(**dct)
        scores = eval_model(0)
        score = np.mean(scores)
        best_score = score

        results = _SimAnnealing_Results(param_types, model, dct, 1.0, scores)
        for n in range(1, n_iter):
            if cooling == 'Exponential':
                temperature = pow(coolarg, n)
            elif cooling == 'Logarithmic':
                temperature = coolarg / math.log(1+n)
            elif cooling == 'Linear':
                temperature = 1 - float(n)/(n_iter+1)
            else:
                raise SyNodeError(
                    'Invalid cooling option "{}" in node'.format(cooling))

            new_idx = np.array(best_par)
            axis = random.randrange(len(params))
            # Non-categorical, use gaussian neighbourhood function
            offset = np.random.randn() / 3
            if decradius:
                offset = offset * np.sqrt(temperature)
            r = int(best_par[axis] + 0.5 + offset*n_params[axis])
            r = max(0, min(n_params[axis]-1, r))
            new_idx[axis] = r

            dct = param_dict(new_idx)
            model.set_params(**dct)
            scores = eval_model(n)

            score = np.mean(scores)
            if score > best_score:
                prob = 1.0
            else:
                prob = np.exp((score - best_score)/temperature)
            changed = False
            if random.random() <= prob:
                best_score = score
                best_par = new_idx
                results.best_estimator_ = copy.deepcopy(model)
                changed = True
            results.update(dct, temperature, scores)
            dct = param_dict(best_par)
            results.update_best(dct, best_score, changed)

        results.cast_to_arrays()
        self.gen_results(node_context, results)
