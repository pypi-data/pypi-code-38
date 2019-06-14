import operator
import os

import numpy as np

from Homevee.Utils import Constants

try:
    import tensorflow as tf
    TENSORFLOW_INSTALLED = True
    #Logger.log("Tensorflow imported")
except:
    TENSORFLOW_INSTALLED = False
    #Logger.log("Error importing Tensorflow")

# These are all parameters that are tied to the particular model architecture
# we're using for Inception v3. These include things like tensor names and their
# sizes. If you want to adapt this script to work with another model, you will
# need to update these to reflect the values in the network you're using.
MAX_NUM_IMAGES_PER_CLASS = 2 ** 27 - 1  # ~134M

class ImageClassifier():
    def __init__(self, model_name):
        self.model_name = model_name

        return

    def load_graph(self, model_file):
        graph = tf.Graph()
        graph_def = tf.GraphDef()
        with open(model_file, "rb") as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)
        return graph

    def read_tensor_from_image_file(self, file_name, input_height=299, input_width=299,
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
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
        normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
        sess = tf.Session()
        result = sess.run(normalized)
        return result

    def load_labels(self, label_file):
        label = []
        proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
        for l in proto_as_ascii_lines:
            label.append(l.rstrip())
        return label

    def predict(self, file_name):
        file_name = os.path.join(Constants.DATA_DIR, file_name)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(BASE_DIR, "tensorflow_data", "models", "mobilenet_v1_1.0_224")
        temp_dir = os.path.join(BASE_DIR, "tensorflow_data", self.model_name)
        model_file = os.path.join(temp_dir, "output_graph.pb")
        label_file = os.path.join(temp_dir, "output_labels.txt")
        input_height = 224
        input_width = 224
        input_mean = 0
        input_std = 255
        input_layer = "input"
        output_layer = "final_result"
        '''if args.graph:
            model_file = args.graph
        if args.labels:
            label_file = args.labels
        if args.input_layer:
            input_layer = args.input_layer
        if args.output_layer:
            output_layer = args.output_layer'''
        graph = self.load_graph(model_file)
        t = self.read_tensor_from_image_file(file_name, input_height=input_height, input_width=input_width,
                                        input_mean=input_mean, input_std=input_std)
        input_name = "import/" + input_layer
        output_name = "import/" + output_layer
        input_operation = graph.get_operation_by_name(input_name)
        output_operation = graph.get_operation_by_name(output_name)
        with tf.Session(graph=graph) as sess:
            results = sess.run(output_operation.outputs[0], {input_operation.outputs[0]: t})
        results = np.squeeze(results)
        top_k = results.argsort()[-5:][::-1]
        labels = self.load_labels(label_file)
        max_val = -1
        max_label = -1
        predictions = []
        for i in top_k:
            predictions.append({'prediction': labels[i], 'confidence': results[i] * 100})
            if (results[i] > max_val):
                max_val = results[i]
                max_label = labels[i]
        # sorting descending by confidence
        sorted_predictions = sorted(predictions, key=operator.itemgetter('confidence'), reverse=True)
        return sorted_predictions