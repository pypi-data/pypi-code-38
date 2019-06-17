__all__ = ['getManager', 'getManagerFromConfig']

import os
import inspect
import superjson

from ExperimentManager.global_manager import global_manager
from ExperimentManager.experiment import ExperimentManager
from ExperimentManager.utils import pprint_dict
from ExperimentManager.gpu_setup import keras_setup
from ExperimentManager.timer import get_timer


def getManager(name = None,experiments_dir = None, project_dir = None, verbose = 1, **kwargs):
    if name is None:
        name = get_call_id()
        if name is None:
            print('WARNING : Could not find an Experiment automatically, creating an empty, dummy experiment manager')
            return getManager(name = 'empty_manager', ghost = True, verbose=verbose)

    if name in global_manager.experiments:
        return global_manager.experiments[name]

    else:
        caller_filename = os.path.abspath(inspect.stack()[1].filename)
        project_dir = project_dir if project_dir is not None else os.path.abspath(os.path.dirname(inspect.stack()[1].filename))
        manager = ExperimentManager(name,experiments_dir = experiments_dir, project_dir = project_dir, verbose = verbose, **kwargs)
        global_manager.add(manager,caller_filename)
        return manager


def getManagerFromConfig(config_file):
    
    if not os.path.isfile(config_file):
        config_file = os.path.join(os.path.dirname(os.path.abspath(inspect.stack()[1].filename)),config_file)
        

    assert os.path.isfile(config_file), 'Config file was not found at {}'.format(config_file)
    config = superjson.json.load(config_file,verbose=False)

    # Looking for gpu setup config

    # if 'gpu' in config:
    #     assert 'devices' in config['gpu']
    #     assert 'allow_growth' in config['gpu']
    #     keras_setup(config['gpu']['devices'],config['gpu']['allow_growth'])

    # Creating the experiment

    assert 'name' in config
    assert not config['name'] in global_manager.experiments

    name = config['name']
    project_dir = os.path.abspath(os.path.dirname(inspect.stack()[1].filename)) if not 'project_dir' in config else config['project_dir']
    experiments_dir = None if not 'experiments_dir' in config else config['experiments_dir']
    verbose = True if not 'verbose' in config else config['verbose']
    
    kwargs = {  key:config[key] for key in ['skip_dirs','ghost','load_dir','tensorboard','gpu_options'] if key in config }
    manager = ExperimentManager(name,experiments_dir = experiments_dir, project_dir = project_dir, verbose = verbose, **kwargs)

    # Adding the entry in the global manager
    caller_filename = os.path.abspath(inspect.stack()[1].filename)
    global_manager.add(manager,caller_filename)

    # Adding a configuration if it exists
    if 'config' in config:
        manager.add_config(config['config'])
    
    # Adding queued commands if exist

    if 'tasks_to_run' in config:
        manager.queue_tasks(config['tasks_to_run'])
        manager.logger.info('Tasks {} added to queue, run manager.run_queue to run them'.format(config['tasks_to_run']))

    return manager


def get_call_id():
    ''' Look through the stack trace for to retrieve a local value in a specific function of a specific file.
    '''	
    
    stack = inspect.stack()

    for i in range(len(stack)-1,-1,-1): # going backwards since the run call should be really early on
        frame = stack[i]
        filename = os.path.abspath(frame.filename)
        if filename in global_manager.callers and 'manager' in frame.frame.f_locals:
            return frame.frame.f_locals['manager'].name
    
    return None