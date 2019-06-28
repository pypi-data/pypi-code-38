#import
import subprocess
import os
import json
import datetime
import inspect
import pickle
from shutil import copyfile

#git
def git_init():
    log_git_init = subprocess.check_output(['git','init'])
    log_git_init = subprocess.check_output(['git','add','.'])
    log_git_init = subprocess.check_output(['git','commit', '-m', '"Initial commit"'])

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'])
 
def get_git_revision_short_hash():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])

def git_commit(time):    
    log_git_commit = subprocess.check_output(['git','add','.'])
    log_git_commit = subprocess.check_output(['git','commit', '-m', time])

#universe
def discover(universe):
        universe = 'multiverse/' + str(universe)
        if not os.path.exists(universe):
                os.makedirs(universe)
        return universe


#timeline
def timeline(universe, rev_hash, rev_short_hash):
        timeline = str(universe) + '/' + rev_short_hash.decode("utf-8").replace('\n','')
        if not os.path.exists(timeline):
                os.makedirs(timeline)
        return timeline

#metrics
def metrics(universe, model, metrics, param):

    #Git init
    try:
        get_git_revision_hash()
    except:
        git_init()

    #discover Universe
    universe = discover(universe)

    #start Timeline by commit ID
    rev_short_hash = timeline(universe, get_git_revision_hash(), get_git_revision_short_hash())

    #define Way
    metric_path = str(rev_short_hash) + '/'
    metric_file = str(model['name']) + '.json'

    #set point in Spacetime
    time = datetime.datetime.now()
    time = time.strftime("%H:%M:%S %d/%m/%Y")

    #log timetravel
    frame_info = inspect.stack()[1]
    filename = frame_info[1]

    #params
    info = {
        'file': filename,
        'model': model['name'],
        'metrics': metrics,
        'time': time,
        'param': param
    }

    #pickle
    model_file = metric_path + str(model['name']) + '.pkl'
    pickle.dump(model['model'], open(model_file, 'wb'))

    #register
    if os.path.isfile(metric_path + metric_file):
        with open(metric_path + metric_file, 'a+') as json_file:  
            json.dump(info, json_file, indent=4)
    else:
        with open(metric_path + metric_file, 'w') as json_file:
            json.dump(info, json_file, indent=4)

    git_commit(time)
                
#elegible_reality

#reality
def access_reality(reality): 
    filename_w_ext = os.path.basename(reality)
    reality_name, reality_extension = os.path.splitext(filename_w_ext)
    address, reality_filename_complete = os.path.split(reality)
    micro_address, timeline = os.path.split(address)
    nano_address, universe = os.path.split(micro_address)
    print('Access reality "{}" from timeline "{}" from universe "{}"'.format(reality_name,timeline, universe))
    reality_path = micro_address + '/reality/'
    if not os.path.exists(reality_path):
        os.makedirs(reality_path)
    new_reality = reality_path + reality_filename_complete
    copyfile(reality, new_reality)
