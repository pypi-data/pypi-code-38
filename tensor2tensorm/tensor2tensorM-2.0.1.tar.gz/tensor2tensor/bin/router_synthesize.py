# Enable TF Eager execution


#----MY----
import os
from flask import request
from flask import jsonify
from flask import Blueprint
import gc


import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import os
import collections
import base64
from io import StringIO
import pydub
import shutil
from scipy.io import wavfile

import IPython
# import google.colab
#
from tensor2tensor import models
from tensor2tensor import problems
from tensor2tensor.layers import common_layers
from tensor2tensor.utils import trainer_lib
from tensor2tensor.utils import t2t_model
from tensor2tensor.utils import registry
from tensor2tensor.utils import metrics

# Enable TF Eager execution
from tensorflow.contrib.eager.python import tfe
tfe = tf.contrib.eager
tfe.enable_eager_execution()

# Other setup
Modes = tf.estimator.ModeKeys

router_synthesize = Blueprint('synthesize', __name__)
#@simple_page.route('/<page>')
#app = Flask(__name__)
@router_synthesize.route('/stt/synthesize',methods=['POST'])
def stt_synthesize():


    try:
        data = {}
        data['Parameters'] = []
        data['Response'] = []

        params = [['data_dir', "",'Data directory.'],
                  ['checkpoint_dir', None, 'Directory where the checkpoint are stored'],
                  ['problem_name', '', 'The name of the problem to generate data for.'],
                  ['file','','File directory to synthesize'],
                  ['dir_file','Directory path of file']]

        values = request.get_json()

        for xParams in params:
            if xParams[0] not in values:
                parameters = {}
                parameters['Parameter'] = xParams[0]
                parameters['Info'] = 'The parameter, has not been entered'
                parameters['Default_value_' + xParams[0]] = xParams[1]
                parameters['About_' + xParams[0]] = xParams[2]
                data['Parameters'].append(parameters)


        if values['file'] == '':
            raise ValueError('Enter a valid file')

        if values['dir_file'] == '':
            raise ValueError('Enter a valid file directory')


        # Setup some directories
        data_dir = values['data_dir']
        checkpoint_dir = values['checkpoint_dir']
        # usr_dir = "/home/manuel_garcia02/tensor2tensor/tensor2tensor/data_generators/"
        # tf.gfile.MakeDirs(data_dir)

        problem_name = values['problem_name']
        asr_problem = problems.problem(problem_name)
        encoders = asr_problem.feature_encoders(None)

        model_name = "transformer"
        hparams_set = "transformer_librispeech_tpu"




        hparams = trainer_lib.create_hparams(hparams_set, data_dir=data_dir, problem_name=problem_name)
        asr_model = registry.model(model_name)(hparams, Modes.PREDICT)





        def encode(x):
            print('inputs')
            waveforms = encoders["waveforms"].encode(x)
            print(waveforms)
            print('problem')
            print(asr_problem)
            encoded_dict = asr_problem.preprocess_example({"waveforms": waveforms, "targets": []}, Modes.PREDICT,
                                                          hparams)
            print('encoded_dict')
            print(encoded_dict)

            print('return encode')
            print({"inputs": tf.expand_dims(encoded_dict["inputs"], 0),
                    "targets": tf.expand_dims(encoded_dict["targets"], 0)})
            return {"inputs": tf.expand_dims(encoded_dict["inputs"], 0),
                    "targets": tf.expand_dims(encoded_dict["targets"], 0)}

        def decode(integers):
            integers = list(np.squeeze(integers))
            print('integers')
            print(integers)
            if 1 in integers:
                integers = integers[:integers.index(1)]
                print('integers')
                print(integers)
                print('encoder return')
                print(encoders["targets"].decode(np.squeeze(integers)))
            return encoders["targets"].decode(np.squeeze(integers))

        # Copy the pretrained checkpoint locally
        gs_ckpt = os.path.join(checkpoint_dir)
        ckpt_path = tf.train.latest_checkpoint(os.path.join(checkpoint_dir))

        # Restore and transcribe!
        def transcribe(inputs):
            encoded_inputs = encode(inputs)
            print('encoded_inputs in transcribe')
            print(encoded_inputs['inputs'])
            with tfe.restore_variables_on_create(ckpt_path):
                print('asr_model')
                print(asr_model)
                print('fin asr')
                model_output = asr_model.infer(encoded_inputs, beam_size=2, alpha=0.6, decode_length=1)
                # print('model_output')
                # print(model_output)
                print('model_output["outputs"]')
                print(model_output["outputs"])
            return decode(model_output["outputs"])

        def play_and_transcribe(inputs):
            waveforms = encoders["waveforms"].encode(inputs)
            IPython.display.display(IPython.display.Audio(data=waveforms, rate=16000))
            return transcribe(inputs)

        data['Response'].append({'Info': 'Sinthezise'})

        prerecorded_messages = []
        save_filename = os.path.join(os.path.abspath(values['dir_file']), values['file'])



        prerecorded_messages.append(save_filename)

        input = ''
        output = ''

        for inputs in prerecorded_messages:
            outputs = play_and_transcribe(inputs)
            # global input
            # global output
            # input = inputs
            # output = outputs
            data['Response'].append({'Input': inputs})
            data['Response'].append({'Output': outputs})
            print("Inputs: %s" % inputs)
            print("Outputs: %s" % outputs)

        gc.collect()

        return jsonify(data)
    except Exception as e:
        print('Ocurrio un error: ' + str(e))
        return jsonify(service='Ocurrió un error: ' + str(e))
