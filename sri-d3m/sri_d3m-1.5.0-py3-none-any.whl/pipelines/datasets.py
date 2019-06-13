import json
import os

from sri.pipelines.parsed_datasets import ALL_DATASETS

# Datasets that are slow because of their size (on disk or number of records).
if (os.environ.get('EXCLUDE_SLOW_DATASETS') is not None):
    SLOW_DATASETS = {
        'uu3_world_development_indicators',
        '6_70_com_amazon',
        '6_86_com_DBLP',
        '1567_poker_hand',
        '60_jester',
        'LL1_336_MS_Geolife_transport_mode_prediction',
        'LL1_penn_fudan_pedestrian',
        'LL1_VTXC_1343_cora',
    }
else:
    SLOW_DATASETS = set()

GRAPH_TASKS = {
    'communityDetection',
    'graphMatching',
    'linkPrediction',
    'vertexClassification',
    'vertexNomination',
}

# Datasets that are broken for one reason or another.
BLACKLIST = {
    'LL1_336_MS_Geolife_transport_mode_prediction',
    'LL1_336_MS_Geolife_transport_mode_prediction_separate_lat_lon',
}

for i in reversed(range(len(ALL_DATASETS))):
    if (ALL_DATASETS[i]['name'] in BLACKLIST):
        ALL_DATASETS.pop(i)

def get_dataset(name):
    for dataset in ALL_DATASETS:
        if (dataset['name'] == name):
            return dataset
    raise LookupError("Could not find a dataset with name: %s" % (name))

def get_dataset_names():
    return [dataset['name'] for dataset in ALL_DATASETS]

def get_problem_id(name):
    return get_dataset(name)['problem_id']

def get_full_dataset_id(name):
    return get_dataset(name)['dataset_id']

def get_train_dataset_id(name):
    return get_dataset(name)['train_dataset_id']

def get_test_dataset_id(name):
    return get_dataset(name)['test_dataset_id']

def get_score_dataset_id(name):
    return get_dataset(name)['score_dataset_id']

def get_size(name):
    return get_dataset(name)['size']

def get_graph_dataset_names():
    names = []

    for dataset in ALL_DATASETS:
        if (dataset['task_type'] in GRAPH_TASKS):
            names.append(dataset['name'])

    return names

def get_dataset_names_by_task(task_type):
    names = []

    for dataset in ALL_DATASETS:
        if (dataset['name'] in SLOW_DATASETS):
            continue

        if (task_type == dataset['task_type']):
            names.append(dataset['name'])

    return names
