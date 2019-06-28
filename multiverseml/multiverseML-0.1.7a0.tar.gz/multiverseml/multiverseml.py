#import
import subprocess
import os
import json
import datetime
import inspect
import pickle
from shutil import copyfile
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify


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
                
#path reality
def space_fold(reality):
    filename_w_ext = os.path.basename(reality)
    reality_name, reality_extension = os.path.splitext(filename_w_ext)
    address, reality_filename_complete = os.path.split(reality)
    micro_address, timeline = os.path.split(address)
    nano_address, universe = os.path.split(micro_address)
    reality_path = micro_address + '/reality/'
    new_reality = reality_path + 'reality' + reality_extension
    return new_reality, reality_name, reality_extension, reality_filename_complete, reality_path, micro_address, nano_address, address, timeline, universe

#reality http
def worm_hole(reality):
    new_reality, reality_name, reality_extension, reality_filename_complete, reality_path, micro_address, nano_address, address, timeline, universe = space_fold(reality)

    server = '''
import numpy as np
from flask import Flask, request, jsonify
import pickle
import pandas as pd
app = Flask(__name__)
model = pickle.load(open("'''+new_reality+'''","rb"))
way = "/" + str("'''+universe+'''")
@app.route(way,methods=["POST"])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    data = pd.DataFrame(columns = data["columns"], data = [data["data"]])
    # Make prediction using model loaded from disk as per the data.
    prediction = model.predict(data)
    output = prediction[0]
    return jsonify(output)
if __name__ == "__main__":
    app.run(port=5000, debug=True)'''

    with open(reality_path + 'server.py', 'w') as file:
        file.write(server)


#reality
def access_reality(alternative_reality): 
    new_reality, reality_name, reality_extension, reality_filename_complete, reality_path, micro_address, nano_address, address, timeline, universe = space_fold(alternative_reality)
    print('Access reality "{}" from timeline "{}" from universe "{}"'.format(reality_name,timeline, universe))
    if not os.path.exists(reality_path):
        os.makedirs(reality_path)
    copyfile(alternative_reality, new_reality)
    return new_reality

