#import
import subprocess
import os
import json
import datetime

#git
def git_init():
    subprocess.check_output(['git','init'])
    subprocess.check_output(['git','add','.'])
    subprocess.check_output(['git','commit', '-m', '"Initial commit"'])

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'])
 
def get_git_revision_short_hash():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])

def git_commit(time):    
    subprocess.check_output(['git','add','.'])
    subprocess.check_output(['git','commit', '-m', time])

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

    #params
    info = {
        'model': model['name'],
        'metrics': metrics,
        'time': time,
        'param': param
    }

    if os.path.isfile(metric_path + metric_file):
        with open(metric_path + metric_file, 'a+') as json_file:  
            json.dump(info, json_file, indent=4)
    else:
        with open(metric_path + metric_file, 'w') as json_file:
            json.dump(info, json_file, indent=4)

    git_commit(time)
                
#elegible_reality

#reality

