#!/usr/bin/env python
"""Trainer for Tensor2Tensor.

This script is used to train your models in Tensor2Tensor.

For example, to train a shake-shake model on MNIST run this:

t2t-trainer \
  --generate_data \
  --problem=image_mnist \
  --data_dir=~/t2t_data \
  --tmp_dir=~/t2t_data/tmp
  --model=shake_shake \
  --hparams_set=shake_shake_quick \
  --output_dir=~/t2t_train/mnist1 \
  --train_steps=1000 \
  --eval_steps=100
"""


#----MY----
import os
import sys
from flask import request
from flask import jsonify
from flask import Blueprint
import argparse
import threading

router_train = Blueprint('train', __name__)
#@simple_page.route('/<page>')
#app = Flask(__name__)
@router_train.route('/stt/train',methods=['POST'])

def stt_train():
    # try:

        # from tensor2tensor.utils import flags as t2t_flags
        # from tensor2tensor.bin import t2t_trainer

        from tensor2tensor.bin import t2t_trainer
        import tensorflow as tf

        flags = tf.flags
        FLAGS = flags.FLAGS

        print(FLAGS.problem)

        parser = argparse.ArgumentParser()
        args = parser.parse_args()

        argv = ''
        data = {}
        data['Parameters'] = []
        data['Information'] = []

        params = [['t2t_usr_dir', "",'Path to a Python module that will be imported. The __init__.py file should include the necessary imports. The imported files should contain registrations, e.g. @registry.register_problem calls, that will then be available to t2t_train.'],
                  ['random_seed', None, 'Random seed.'],
                  ['tpu_num_shards', 8, 'Number of tpu shards.'],
                  ['iterations_per_loop', 100, 'Number of iterations in a TPU training loop.'],
                  ['use_tpu', False, 'Whether to use TPU.'],
                  ['use_tpu_estimator', False, 'Whether to use TPUEstimator. This is always enabled when use_tpu is True.'],
                  ['xla_compile', False, 'Whether to use XLA to compile model_fn.'],
                  ['xla_jit_level', -1, 'GlobalJitLevel to use while compiling the full graph.'],
                  ['tpu_infeed_sleep_secs', None, 'How long to sleep the infeed thread.'],
                  ['generate_data', False, 'Generate data before training?'],
                  ['tmp_dir', '/tmp/t2t_datagen', 'Temporary storage directory, used if --generate_data.'],
                  ['profile', False, 'Profile performance?'],
                  ['inter_op_parallelism_threads', 0, 'Number of inter_op_parallelism_threads to use for CPU. See TensorFlow config.proto for details.'],
                  ['intra_op_parallelism_threads', 0,'Number of intra_op_parallelism_threads to use for CPU. See TensorFlow config.proto for details.'],
                  ['optionally_use_dist_strat', False,'Whether to use TensorFlow DistributionStrategy instead of explicitly replicating the model. DistributionStrategy is used only if the model replication configuration is supported by the DistributionStrategy.'],
                  ['master', '','Address of TensorFlow master.'],
                  ['output_dir', '','Base output directory for run.'],
                  ['schedule', 'continuous_train_and_eval','Method of Experiment to run.'],
                  ['eval_steps', 100,'Number of steps in evaluation. By default, eval will stop after eval_steps or when it runs through the eval dataset once in full, whichever comes first, so this can be a very large number.'],
                  ['std_server_protocol', 'grpc','Protocol for tf.train.Server.'],
                  ['cloud_tpu_name', '%s-tpu' % os.getenv("USER"),'Name of Cloud TPU instance to use or create.'],
                  ['cloud_mlengine', False,'Whether to launch on Cloud ML Engine.'],
                  ['cloud_mlengine_master_type', None,'Machine type for master on Cloud ML Engine. If provided, overrides default selections based on --worker_gpu. User is responsible for ensuring type is valid and that --worker_gpu matches number of GPUs on machine type. See documentation: https://cloud.google.com/ml-engine/reference/rest/v1/projects.jobs#traininginput'],
                  ['autotune_objective', None,'TensorBoard metric name to optimize.'],
                  ['autotune_maximize', True,'Whether to maximize (vs. minimize) autotune_objective.'],
                  ['autotune_max_trials', 10,'Maximum number of tuning experiments to run.'],
                  ['autotune_parallel_trials', 1,'How many trials to run in parallel (will spin up this many jobs.'],
                  ['job-dir', None,'DO NOT USE. Exists only for Cloud ML Engine to pass in during hyperparameter tuning. Overrides --output_dir.'],
                  ['log_step_count_steps', 100,'Number of local steps after which progress is printed out']]

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


        for value in values:
            FLAGS.__setattr__(value, values[value])
            sys.argv.append('--{}={}'.format(value, values[value]))
            # sys.argv.__setattr__(value, values[value])


        data['Information'].append({'Info': 'Entrenando'})

        def start():
            start_train(argv,tf,FLAGS,t2t_trainer)




        t = threading.Thread(target=start, name='Proceso')
        t.start()
        return jsonify(data)

    # except Exception as e:
    #     print('Ocurrio un error: ' + str(e))
    #     return jsonify(service='Ocurrió un error: ' + str(e))

def start_train(argv,tf, FLAGS, t2t_trainer):
    print(FLAGS.problem)

    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run(t2t_trainer.main(argv))