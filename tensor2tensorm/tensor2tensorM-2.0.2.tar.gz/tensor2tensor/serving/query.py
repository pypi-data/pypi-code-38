# coding=utf-8
# Copyright 2019 The Tensor2Tensor Authors.
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

# """Query an exported model. Py2 only. Install tensorflow-serving-api."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import logging

from oauth2client.client import GoogleCredentials
from six.moves import input  # pylint: disable=redefined-builtin

from tensor2tensor import problems as problems_lib  # pylint: disable=unused-import
from tensor2tensor.serving import serving_utils
from tensor2tensor.utils import registry
from tensor2tensor.utils import usr_dir
from tensor2tensor.utils.hparam import HParams
import tensorflow as tf



#------------------------------
from tensor2tensor import problems
from flask import request
from flask import jsonify
from flask import Blueprint
import wave


flags = tf.flags
FLAGS = flags.FLAGS

flags.DEFINE_string("server", None, "Address to Tensorflow Serving server.")
flags.DEFINE_string("servable_name", None, "Name of served model.")
flags.DEFINE_string("problem", None, "Problem name.")
flags.DEFINE_string("data_dir", None, "Data directory, for vocab files.")
flags.DEFINE_string("t2t_usr_dir", None, "Usr dir for registrations.")
flags.DEFINE_string("inputs_once", None, "Query once with this input.")
flags.DEFINE_integer("timeout_secs", 10, "Timeout for query.")

# For Cloud ML Engine predictions.
flags.DEFINE_string("cloud_mlengine_model_name", None,
                    "Name of model deployed on Cloud ML Engine.")
flags.DEFINE_string(
    "cloud_mlengine_model_version", None,
    "Version of the model to use. If None, requests will be "
    "sent to the default version.")


logger_T2T = logging.getLogger('T2T')


if 'PYTHON_ENV' not in os.environ:
    HOST_TENSORFLOW = 'localhost'
    PORT_TENSORFLOW = '9000'
    MODEL_NAME = 'servex'
    MODEL_BASE_PATH = 'checkpoint/export'
    PROBLEM = 'deepspeech'
    DATA_DIR = 'gs://servex-tensor/data'

else:
    HOST_TENSORFLOW = str(os.environ['HOST_TENSORFLOW'])
    PYTHON_ENV = str(os.environ['PYTHON_ENV'])
    PORT_TENSORFLOW = str(os.environ['PORT_TENSORFLOW'])
    MODEL_NAME = str(os.environ['MODEL_NAME'])
    MODEL_BASE_PATH = str(os.environ['MODEL_BASE_PATH'])
    PROBLEM = str(os.environ['PROBLEM'])
    DATA_DIR = str(os.environ['DATA_DIR'])

def validate_flags():
  """Validates flags are set to acceptable values."""
  if FLAGS.cloud_mlengine_model_name:
    assert not FLAGS.server
    assert not FLAGS.servable_name
  else:
    assert FLAGS.server
    assert FLAGS.servable_name


def make_request_fn():
  """Returns a request function."""
  if FLAGS.cloud_mlengine_model_name:
    request_fn = serving_utils.make_cloud_mlengine_request_fn(
        credentials=GoogleCredentials.get_application_default(),
        model_name=FLAGS.cloud_mlengine_model_name,
        version=FLAGS.cloud_mlengine_model_version)
  else:

    request_fn = serving_utils.make_grpc_request_fn(
        servable_name=FLAGS.servable_name,
        server=FLAGS.server,
        timeout_secs=FLAGS.timeout_secs)
  return request_fn

def error_function(error):
    response = jsonify(
        status=0,
        error=error
    )
    return response

FLAGS.server = HOST_TENSORFLOW + ':' + PORT_TENSORFLOW
FLAGS.servable_name = MODEL_NAME
FLAGS.problem = PROBLEM
FLAGS.data_dir = DATA_DIR

tf.logging.set_verbosity(tf.logging.INFO)
validate_flags()
usr_dir.import_usr_dir(FLAGS.t2t_usr_dir)
problem = registry.problem(FLAGS.problem)
hparams = HParams(
    data_dir=os.path.expanduser(FLAGS.data_dir))
problem.get_hparams(hparams)
request_fn = make_request_fn()


router_synthesize = Blueprint('synthesize', __name__)
@router_synthesize.route('/stt/synthesize', methods=['POST'])
def stt_train():
    global response
    response = ''
    try:
        logger_T2T.debug('Body request: ' + str(request.files))
        data = {}
        data['Response'] = []
        global error
        error = ''
        print(request.files['file'])
        if 'file' not in request.files:
            error = 'Enter a valid key'
            response = error_function(error)
            logger_T2T.error('error: ' + error)
        elif request.files['file'] == '':
            error = 'Enter a valid audio'
            response = error_function(error)
            logger_T2T.error('error: ' + error)
        elif str(request.files['file']).find('.wav') < 1:
            error = 'Enter a valid audio. The file extension should be .wav'
            response = error_function(error)
            logger_T2T.error('error: ' + error)
        else:
            file = request.files['file']
            audio = file.read()
            audio_file_name = os.path.join(os.path.abspath('./'),'temp/temp-' + file.filename)

            with open(audio_file_name, 'wb') as out:
                # Write the request to the file.
                out.write(audio)


            with wave.open(audio_file_name, "rb") as wave_file:
                frame_rate = wave_file.getframerate()

            if str(frame_rate) != '16000':
                error = 'Enter a valid audio. The file sample rate should be 16000'
                response = error_function(error)
                logger_T2T.error('error: ' + error)
            else:

                inputs = audio_file_name
                outputs = serving_utils.predict([inputs], problem, request_fn)
                outputs, = outputs
                output, score = outputs
                data_synthesize = {'Input': str(file.filename), 'Output':str(output), 'Score': str(score)}
                logger_T2T.info('Result synthesize: ' + str(data_synthesize))
                data['Response'].append({'synthesize_info': data_synthesize})
                response = jsonify(
                    status=200,
                    data=data
                )
            os.remove(audio_file_name)

    except Exception as e:
        logger_T2T.error('An error occurred: ' + str(e))
        logger_T2T.warning('Response: ' + str(jsonify(status=0, data="null")))
        response = error_function(str(e))
    return response

