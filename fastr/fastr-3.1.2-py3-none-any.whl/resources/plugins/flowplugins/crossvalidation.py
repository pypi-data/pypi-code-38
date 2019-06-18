# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import fastr
from fastr.core.samples import SampleIndex, SampleItem
from fastr.plugins import FlowInterface


def kfold(n_items, n_folds):
    items_per_fold = n_items // n_folds
    remaining_items = n_items % n_folds
    fold_sizes = [items_per_fold + 1 if x < remaining_items else items_per_fold for x in range(n_folds)]
    return [(list(range(0, sum(fold_sizes[:x]))) + list(range(sum(fold_sizes[:x+1]), n_items)), list(range(sum(fold_sizes[:x]), sum(fold_sizes[:x+1])))) for x in range(n_folds)]


class CrossValidation(FlowInterface.flow_plugin_type):
    """
    Advanced flow plugin that generated a cross-validation data flow. The node
    need an input with data and an input number of folds. Based on that the
    outputs test and train will be supplied with a number of data sets.
    """
    @staticmethod
    def execute(payload):
        log_data = None

        items = payload['items']
        method = sum(x.data for x in payload['method']).sequence_part()
        number_of_folds = sum(x.data for x in payload['number_of_folds']).sequence_part()
        labels = None

        if len(method) != 1:
            raise ValueError('Can only handle 1 method for cross validation!')
        method = method[0].value

        if len(number_of_folds) != 1:
            raise ValueError('Can only handle 1 number_of_folds for cross validation!')
        number_of_folds = number_of_folds[0].value

        fastr.log.debug('CV Plugin items: {!r}'.format(items))
        fastr.log.info('CV Plugin method: {!r}'.format(method))
        fastr.log.info('CV Plugin number_of_folds: {!r}'.format(number_of_folds))

        if labels is not None and len(labels) != len(items):
            raise ValueError('If given, the number of labels should match the number of items!')

        if method == 'KFold':
            cv_iterator = kfold(len(items), n_folds=number_of_folds)
        else:
            raise ValueError('Invalid method selected!')

        train_data = {}
        test_data = {}

        for fold, (train, test) in enumerate(cv_iterator):
            fold_id = 'fold_{}'.format(fold)

            for k, index in enumerate(train):
                item = items[index]
                new_index = SampleIndex([k, fold])
                new_id = item.id + fold_id

                train_data[new_index, new_id] = SampleItem(new_index, new_id, item.data, item.jobs)

            for k, index in enumerate(test):
                item = items[index]
                new_index = SampleIndex([k, fold])
                new_id = item.id + fold_id

                test_data[new_index, new_id] = SampleItem(new_index, new_id, item.data, item.jobs)

        result_data = {'train': train_data, 'test': test_data}

        for key, value in result_data.items():
            values = [(x.id, x.index, x.data) for x in value.values()]
            fastr.log.debug('Result data {}: {}'.format(key, values))

        return result_data, log_data
