#!/usr/bin/env python
"""Data generation for Tensor2Tensor.

This script is used to generate data to train your models
for a number problems for which open-source data is available.

For example, to generate data for MNIST run this:

t2t-datagen \
  --problem=image_mnist \
  --data_dir=~/t2t_data \
  --tmp_dir=~/t2t_data/tmp
"""


#----MY----
from flask import request
from flask import jsonify
from flask import Blueprint
import argparse
import threading
import os


router_datagen = Blueprint('datagen', __name__)
#@simple_page.route('/<page>')
#app = Flask(__name__)
@router_datagen.route('/stt/datagen',methods=['POST'])

def stt_datagen():
    try:


        from tensor2tensor.bin import t2t_datagen

        import tensorflow as tf
        flags = tf.flags
        FLAGS = flags.FLAGS

        parser = argparse.ArgumentParser()
        args = parser.parse_args()

        argv = ''
        data = {}
        data['Parameters'] = []
        data['Information'] = []

        params = [['data_dir', '', 'Data directory.'],
                  ['tmp_dir', '/mnt/disks/mnt-dir/t2t_tmp/', 'Temporary storage directory.'],
                  ['problem', '', 'The name of the problem to generate data for.'],
                  ['exclude_problems', '', 'omma-separates list of problems to exclude.'],
                  ['num_shards', 0, 'How many shards to use. Ignored for registered Problems.'],
                  ['max_cases', 0, 'Maximum number of cases to generate (unbounded if 0).'],
                  ['only_list', False, 'If true, we only list the problems that will be generated.'],
                  ['random_seed', 429459, 'Random seed to use.'],
                  ['task_id', -1, 'For distributed data generation.'],
                  ['task_id_start', -1, 'For distributed data generation.'],
                  ['task_id_end', -1, 'For distributed data generation.'],
                  ['num_concurrent_processes', None, 'Applies only to problems for which multiprocess_generate=True.'],
                  ['t2t_usr_dir', "",'Path to a Python module that will be imported. The __init__.py file should include the necessary imports. The imported files should contain registrations, e.g. @registry.register_problem calls, that will then be available to t2t_gendata.']]

        values = request.get_json()



        for xParams in params:
            if xParams[0] not in values:
                parameters = {}
                parameters['Parameter'] = xParams[0]
                parameters['Info'] = 'The parameter, has not been entered'
                parameters['Default_value_' + xParams[0]] = xParams[1]
                parameters['About_' + xParams[0]] = xParams[2]
                data['Parameters'].append(parameters)

                args.__setattr__(xParams[0], xParams[1])
            else:
                args.__setattr__(xParams[0], values[xParams[0]])
                FLAGS.__setattr__(xParams[0], values[xParams[0]])

        data['Information'].append({'Info': 'Generando datos'})

        def start():
            os.system("gsutil -m cp -r " + args.data_dir + " " + args.tmp_dir )
            t2t_datagen.main(argv)

        t = threading.Thread(target=start, name='Proceso')
        t.start()
        return jsonify(data)

    except Exception as e:
        print('Ocurrio un error: ' + str(e))
        return jsonify(service='Ocurrió un error: ' + str(e))
