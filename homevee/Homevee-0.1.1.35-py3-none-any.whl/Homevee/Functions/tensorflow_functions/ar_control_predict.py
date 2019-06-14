#!/usr/bin/env python
# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#		 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os
from operator import itemgetter

import numpy as np

try:
    import tensorflow as tf
    TENSORFLOW_INSTALLED = True
    #Logger.log("Tensorflow imported")
except:
    TENSORFLOW_INSTALLED = False
    #Logger.log("Error importing Tensorflow")

from Homevee.Utils import Constants


def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
                                input_mean=0, input_std=255):
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(file_reader, channels=3, name='png_reader')
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(tf.image.decode_gif(file_reader, name='gif_reader'))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
    else:
        image_reader = tf.image.decode_jpeg(file_reader, channels=3, name='jpeg_reader')
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0);
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result

def load_labels(label_file):
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label

def predict(file_name):

    file_name = os.path.join(Constants.DATA_DIR, file_name)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(BASE_DIR, "tensorflow_data", "models", "mobilenet_v1_1.0_224")
    temp_dir = os.path.join(BASE_DIR, "tensorflow_data", "ar_control_temp")

    model_file = os.path.join(temp_dir, "output_graph.pb")
    label_file = os.path.join(temp_dir, "output_labels.txt")

    input_height = 224
    input_width = 224
    input_mean = 0
    input_std = 255
    input_layer = "input"
    output_layer = "final_result"

    #output_layer = "output"

    '''if args.graph:
        model_file = args.graph
    if args.labels:
        label_file = args.labels
    if args.input_layer:
        input_layer = args.input_layer
    if args.output_layer:
        output_layer = args.output_layer'''

    graph = load_graph(model_file)
    t = read_tensor_from_image_file(file_name, input_height=input_height, input_width=input_width,
                                    input_mean=input_mean, input_std=input_std)

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name);
    output_operation = graph.get_operation_by_name(output_name);

    with tf.Session(graph=graph) as sess:
        results = sess.run(output_operation.outputs[0], {input_operation.outputs[0]: t})
    results = np.squeeze(results)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(label_file)

    max_val = -1
    max_label = -1

    predictions = []

    for i in top_k:
        #Logger.log(labels[i], results[i])

        predictions.append({'prediction': labels[i], 'confidence': results[i]*100})

        if (results[i] > max_val):
            max_val = results[i]
            max_label = labels[i]

    #sorting descending by confidence
    sorted_predictions = sorted(predictions, key=itemgetter('confidence'), reverse=True)

    #max_val = max_val * 100

    #return (max_label, max_val)

    return sorted_predictions