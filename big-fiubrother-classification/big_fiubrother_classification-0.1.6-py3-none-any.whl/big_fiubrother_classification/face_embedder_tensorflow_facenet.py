import cv2
import tensorflow as tf
from tensorflow.python.platform import gfile
import numpy as np
import sys
import os
import re

class FaceEmbedderTensorflowFacenet:

    def __init__(self):

        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Create TensorFlow Graph
        self.tf_graph = tf.Graph()
        self.tf_graph.as_default()

        # Create TensorFlow Session
        self.tf_session = tf.Session()

        # Load the model
        self.model_path = dir_path + "/model/20170512-110547"
        self._load_model(self.model_path)

        # Get input and output tensors
        self.images_tensor = tf.get_default_graph().get_tensor_by_name("input:0")
        self.train_phase_tensor = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        self.embeddings_tensor = tf.get_default_graph().get_tensor_by_name("embeddings:0")

    def close(self):
        pass

    def _load_model(self, model, input_map=None):
        # Check if the model is a model directory (containing a metagraph and a checkpoint file)
        #  or if it is a protobuf file with a frozen graph
        model_exp = os.path.expanduser(model)
        if (os.path.isfile(model_exp)):
            print('Model filename: %s' % model_exp)
            with gfile.FastGFile(model_exp, 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, input_map=input_map, name='')
        else:
            print('Model directory: %s' % model_exp)
            meta_file, ckpt_file = self._get_model_filenames(model_exp)

            print('Metagraph file: %s' % meta_file)
            print('Checkpoint file: %s' % ckpt_file)

            saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file), input_map=input_map)
            saver.restore(self.tf_session, os.path.join(model_exp, ckpt_file))

    def _get_model_filenames(self, model_dir):
        files = os.listdir(model_dir)
        meta_files = [s for s in files if s.endswith('.meta')]
        if len(meta_files) == 0:
            raise ValueError('No meta file found in the model directory (%s)' % model_dir)
        elif len(meta_files) > 1:
            raise ValueError('There should not be more than one meta file in the model directory (%s)' % model_dir)
        meta_file = meta_files[0]
        ckpt = tf.train.get_checkpoint_state(model_dir)
        if ckpt and ckpt.model_checkpoint_path:
            ckpt_file = os.path.basename(ckpt.model_checkpoint_path)
            return meta_file, ckpt_file

        meta_files = [s for s in files if '.ckpt' in s]
        max_step = -1
        for f in files:
            step_str = re.match(r'(^model-[\w\- ]+.ckpt-(\d+))', f)
            if step_str is not None and len(step_str.groups()) >= 2:
                step = int(step_str.groups()[1])
                if step > max_step:
                    max_step = step
                    ckpt_file = step_str.groups()[0]
        return meta_file, ckpt_file

    def _prewhiten_image(self, x):
        mean = np.mean(x)
        std = np.std(x)
        std_adj = np.maximum(std, 1.0 / np.sqrt(x.size))
        y = np.multiply(np.subtract(x, mean), 1 / std_adj)
        return y

    def _preprocess_image(self, img):
        img_list = []
        prewhitened = self._prewhiten_image(img)
        img_list.append(prewhitened)
        images = np.stack(img_list)
        return images

    def _load_image(self, image_path):

        img = cv2.imread(os.path.expanduser(image_path))
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def get_embedding(self, image_path):

        img = self._load_image(image_path)

        return self.get_embedding_mem(img)

    def get_embedding_mem(self, cv_image):

        # preprocess
        image = self._preprocess_image(cv_image)

        # Run forward pass to calculate embeddings
        feed_dict = {self.images_tensor: image, self.train_phase_tensor: False}
        result = self.tf_session.run(self.embeddings_tensor, feed_dict=feed_dict)
        return result[0]

