# ================================================================================ #
#   Authors: Fabio Frazao and Oliver Kirsebom                                      #
#   Contact: fsfrazao@dal.ca, oliver.kirsebom@dal.ca                               #
#   Organization: MERIDIAN (https://meridian.cs.dal.ca/)                           #
#   Team: Data Analytics                                                           #
#   Project: ketos                                                                 #
#   Project goal: The ketos library provides functionalities for handling          #
#   and processing acoustic data and applying deep neural networks to sound        #
#   detection and classification tasks.                                            #
#                                                                                  #
#   License: GNU GPLv3                                                             #
#                                                                                  #
#       This program is free software: you can redistribute it and/or modify       #
#       it under the terms of the GNU General Public License as published by       #
#       the Free Software Foundation, either version 3 of the License, or          #
#       (at your option) any later version.                                        #
#                                                                                  #
#       This program is distributed in the hope that it will be useful,            #
#       but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#       GNU General Public License for more details.                               # 
#                                                                                  #
#       You should have received a copy of the GNU General Public License          #
#       along with this program.  If not, see <https://www.gnu.org/licenses/>.     #
# ================================================================================ #

""" CNN module within the ketos library

    This module provides utilities to work with Convolutional 
    Neural Networks for classification tasks.

    Contents:
        DataHandler class:
        DataUse class:
"""

import tensorflow as tf
import numpy as np
import pandas as pd
from collections import namedtuple
from ketos.neural_networks.neural_networks import DataHandler, DataUse, predictions, class_confidences
from ketos.data_handling.data_handling import from1hot, to1hot, get_image_size
from ketos.data_handling.data_feeding import ActiveLearningBatchGenerator


ConvParams = namedtuple('ConvParams', 'name n_filters filter_shape')
ConvParams.__doc__ = '''\
Name and dimensions of convolutional layer in neural network

name - Name of convolutional layer, e.g. "conv_layer"
n_filters - Number of filters, e.g. 16
filter_shape - Filter shape, e.g. [4,4]'''


class BasicCNN(DataHandler):
    """ Convolutional Neural Network for classification tasks.

        The network architecture can only be constructed if the shape of the input data is known.
        Therefore, either image_shape or train_x must be provided.
        In the latter case, the shape is automatically determined from the input data.

        Args:
            image_shape: tuple
                Shape of input images
            train_x: numpy array
                Training data
            train_y: numpy array
                Labels for training data. Can be integers or 1-hot encoded
            validation_x: numpy array
                Validation data
            validation_y: numpy array
                Labels for validation data. Can be integers or 1-hot encoded
            test_x: numpy array
                Test data
            test_y: numpy array
                Labels for test data. Can be integers or 1-hot encoded
            num_labels: int
                Number of labels
            batch_size: int
                The number of examples in each batch
            num_epochs: int
                The number of epochs
            learning_rate: float
                The learning rate to be using by the optimization algorithm
            keep_prob: float
                Probability of keeping weights during training. Set keep_prob to 1.0 to disable drop-out (default).
            seed: int
                Seed to be used by both tensorflow and numpy when generating random numbers            
            verbosity: int
                Verbosity level (0: no messages, 1: warnings only, 2: warnings and diagnostics)
            max_frames: int
                Maximum number of frames that will be acted on by a tensorflow operation at a time.
                Useful to avoid memory warnings/errors.

        Attributes:
            learning_rate_value: float
                The learning rate to be using by the optimization algorithm
            keep_prob_value: float
                Probability of keeping weights during training. Set keep_prob to 1.0 to disable drop-out (default).
            sess: tf.Session
                Current TensorFlow session
            epoch_counter: int
                Keeps count of the current training epoch
            image_shape: tuple
                Shape of input data                

        Example:

            >>> # initialize BasicCNN for classifying 2x2 images
            >>> from ketos.neural_networks.cnn import BasicCNN
            >>> cnn = BasicCNN(image_shape=(2,2))
            >>> print(cnn.image_shape)
            (2, 2)
    """
    def __init__(self, image_shape=None, train_x=None, train_y=None, 
                validation_x=None, validation_y=None, test_x=None, test_y=None, 
                num_labels=2, batch_size=128, num_epochs=10, learning_rate=0.01, 
                keep_prob=1.0, seed=42, verbosity=2, max_frames=1E4):

        assert (image_shape is not None) or (train_x is not None), "image_shape or train_x must be provided"

        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.learning_rate_value = learning_rate
        self.keep_prob_value = keep_prob
        self.set_seed(seed)
        self.verbosity = verbosity
        self.max_frames = max_frames

        self.sess = tf.Session()
        self.epoch_counter = 0

        super(BasicCNN, self).__init__(train_x=train_x, train_y=train_y, 
                validation_x=validation_x, validation_y=validation_y,
                test_x=test_x, test_y=test_y, num_labels=num_labels)

        if train_x is not None:
            self.image_shape = self._image_shape()
        else:
            self.image_shape = image_shape

    def reset(self):
        """ Reset the state of the network.

            Resets the epoch counter to 0 and reinitializes all weights to random values.
        """
        self.epoch_counter = 0
        self.sess.run(self.init_op)

    def set_tf_nodes(self, tf_nodes, reset=True):
        """ Set the nodes of the tensorflow graph as instance attributes, so that other methods can access them

            Args:
                tf_nodes: dict
                    A dictionary with the tensorflow objects necessary to train and run the model:
                    sess, x, y, cost_function, optimizer, predict, correct_prediction,
                    accuracy, init_op, merged, writer, saver, keep_prob, learning_rate, class_weights.
                    These objects are stored as instance attributes when the class is instantiated.
                reset: bool
                    Reset the epoch counter and re-initialize the weights

            Returns:
                None
        """
        self.x = tf_nodes['x']
        self.y = tf_nodes['y']
        self.cost_function = tf_nodes['cost_function']
        self.optimizer = tf_nodes['optimizer']
        self.predict = tf_nodes['predict']
        self.correct_prediction = tf_nodes['correct_prediction']
        self.accuracy = tf_nodes['accuracy']
        self.init_op = tf_nodes['init_op']
        self.merged = tf_nodes['merged']
        self.writer = tf_nodes['writer']
        self.saver = tf_nodes['saver']
        self.keep_prob = tf_nodes['keep_prob']
        self.learning_rate = tf_nodes['learning_rate']
        self.class_weights = tf_nodes['class_weights']

        if reset:
            self.reset()

    def set_seed(self,seed):
        """Set the random seed.

            Useful to generate reproducible results.

            Args:
                seed: int
                    Seed to be used by both tensorflow and numpy when generating random numbers
            Returns:
                None        
        """
        np.random.seed(seed)
        tf.set_random_seed(seed)
             
    def set_verbosity(self, verbosity):
        """Set verbosity level.
            
            0: no messages
            1: warnings only
            2: warnings and diagnostics

            Args:
                verbosity: int
                    Verbosity level.        
        """
        self.verbosity = verbosity

    def load(self, saved_meta, checkpoint, reset=False):
        """Load the Neural Network structure and weights from a saved model.

            See the save() method. 

            Args:
                saved_meta: str
                    Path to the saved .meta file.

                checkpoint: str
                    Path to the checkpoint to be used when loading the saved model

                reset: bool
                    Reset weights or use weights from the saved model.

            Returns:
                tf_nodes: dict
                    A dictionary with the tensorflow objects necessary to train and run the model:
                    sess, x, y, cost_function, optimizer, predict, correct_prediction,
                    accuracy, init_op, merged, writer, saver, keep_prob, learning_rate, class_weights.
        """
        sess = self.sess
        restorer = tf.train.import_meta_graph(saved_meta)
        restorer.restore(sess, tf.train.latest_checkpoint(checkpoint))

        graph = tf.get_default_graph()
        x = graph.get_tensor_by_name("x:0")
        y = graph.get_tensor_by_name("y:0")
        cost_function = graph.get_tensor_by_name("cost_function:0")
        optimizer = graph.get_operation_by_name("optimizer")
        predict = graph.get_tensor_by_name("predict:0")
        correct_prediction = graph.get_tensor_by_name("correct_prediction:0")
        accuracy = graph.get_tensor_by_name("accuracy:0")
        keep_prob = graph.get_tensor_by_name("keep_prob:0")        
        learning_rate = graph.get_tensor_by_name("learning_rate:0")      
        class_weights = graph.get_tensor_by_name("class_weights:0")  

        init_op = tf.global_variables_initializer()
        merged = tf.summary.merge_all()
        writer = tf.summary.FileWriter('summaries')
        saver = tf.train.Saver()

        tf_nodes = {'x': x,
                'y':y,            
                'cost_function': cost_function,
                'optimizer': optimizer,
                'predict': predict,
                'correct_prediction':correct_prediction,
                'accuracy': accuracy,
                'init_op': init_op,
                'merged': merged,
                'writer': writer,
                'saver': saver,
                'keep_prob': keep_prob,
                'learning_rate': learning_rate,
                'class_weights': class_weights,
                }

        self.set_tf_nodes(tf_nodes=tf_nodes, reset=reset)

        return tf_nodes

    def create(self, conv_params=[ConvParams(name='conv_1',n_filters=32,filter_shape=[2,8]), ConvParams(name='conv_2',n_filters=64,filter_shape=[30,8])], dense_size=[512]):
        """Create the Neural Network structure.

            The Network has a number of convolutional layers followed by a number 
            of fully connected layers with ReLU activation functions and a final 
            output layer with softmax activation.

            Each new convolutional layer is created with the method _create_new_conv_layer().

            Note that the window used for performing max-pooling on each convolutional layer has 
            the shape [2,2].
            
            The default network structure has two convolutional layers 
            and one fully connected layers with ReLU activation.

            Args:
                conv_params: list(ConvParams)
                    Configuration parameters for the convolutional layers.
                    Each item in the list represents a convolutional layer.
                dense_size: list(int)
                    Sizes of the fully connected layers preceeding the output layer.

            Returns:
                tf_nodes: dict
                    A dictionary with the tensorflow objects necessary to train and run the model:
                    sess, x, y, cost_function, optimizer, predict, correct_prediction,
                    accuracy, init_op, merged, writer, saver, keep_prob, learning_rate, class_weights.

            Example:

                >>> # initialize BasicCNN for classifying 4x4 images
                >>> from ketos.neural_networks.cnn import BasicCNN
                >>> cnn = BasicCNN(image_shape=(4,4), verbosity=2)
                >>> # create a small network with two convolutional layers and one dense layer
                >>> layer1 = ConvParams(name='conv_1', n_filters=4, filter_shape=[2,2])
                >>> layer2 = ConvParams(name='conv_2', n_filters=8, filter_shape=[4,4])
                >>> _ = cnn.create(conv_params=[layer1, layer2], dense_size=[8])
                ======================================================
                                   Convolutional layers               
                ------------------------------------------------------
                  Name   Input x Filters   Filter Shape   Output dim. 
                ------------------------------------------------------
                  conv_1       1 x 4          [2,2]         16
                  conv_2       4 x 8          [4,4]         8
                ======================================================
                                  Fully connected layers              
                ------------------------------------------------------
                  Name       Size                                      
                ------------------------------------------------------
                  dense_1    8
                  class_weights    2
                ======================================================
        """
        input_shape = self._image_shape()
        num_labels = self.num_labels

        keep_prob = tf.placeholder(tf.float32, name='keep_prob')
        learning_rate = tf.placeholder(tf.float32, name='learning_rate')

        x = tf.placeholder(tf.float32, [None, input_shape[0] * input_shape[1]], name="x")
        x_shaped = tf.reshape(x, [-1, input_shape[0], input_shape[1], 1])
        y = tf.placeholder(tf.float32, [None, num_labels], name="y")

        pool_shape=[2,2]

        # input and convolutional layers
        params = [ConvParams(name='input', n_filters=1, filter_shape=[1,1])] # input layer with dimension 1
        params.extend(conv_params)
            
        # dense layers including output layer
        dense_size.append(num_labels)

        # create convolutional layers
        conv_layers = [x_shaped]
        N = len(params)
        conv_summary = list()
        for i in range(1,N):
            # previous layer
            l_prev = conv_layers[len(conv_layers)-1]
            # layer parameters
            n_input = params[i-1].n_filters
            n_filters = params[i].n_filters
            filter_shape = params[i].filter_shape
            name = params[i].name
            # create new layer
            l = self._create_new_conv_layer(l_prev, n_input, n_filters, filter_shape, pool_shape, name=name)
            conv_layers.append(l)
            # collect info
            dim = l.shape[1] * l.shape[2] * l.shape[3]
            conv_summary.append("  {0}       {1} x {2}          [{3},{4}]         {5}".format(name, n_input, n_filters, filter_shape[0], filter_shape[1], dim))
            # apply drop-out 
            drop_out = tf.nn.dropout(l, keep_prob)
            conv_layers.append(drop_out)

        # last layer
        last = conv_layers[-1]

        # flatten
        dim = last.shape[1] * last.shape[2] * last.shape[3]
        flattened = tf.reshape(last, [-1, dim])

        # fully-connected layers with ReLu activation
        dense_layers = [flattened]
        dense_summary = list()
        for i in range(len(dense_size)):
            size = dense_size[i] 
            l_prev = dense_layers[i]
            w_name = 'w_{0}'.format(i+1)
            w = tf.Variable(tf.truncated_normal([int(l_prev.shape[1]), size], stddev=0.03), name=w_name)
            b_name = 'b_{0}'.format(i+1)
            b = tf.Variable(tf.truncated_normal([size], stddev=0.01), name=b_name)
            l = tf.matmul(l_prev, w) + b
            if i < len(dense_size) - 1:
                n = 'dense_{0}'.format(i+1)
                l = tf.nn.relu(l, name=n) # ReLu activation
            else: # output layer
                cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=l, labels=y),name="cost_function")
                n = 'class_weights'
                l = tf.nn.softmax(l, name=n) # softmax                    

            dense_layers.append(l)
            dense_summary.append("  {0}    {1}".format(n, size))

        if self.verbosity >= 2:
            print('======================================================')
            print('                   Convolutional layers               ')
            print('------------------------------------------------------')
            print('  Name   Input x Filters   Filter Shape   Output dim. ')
            print('------------------------------------------------------')
            for line in conv_summary:
                print(line)
            print('======================================================')
            print('                  Fully connected layers              ')
            print('------------------------------------------------------')
            print('  Name       Size                                      ')
            print('------------------------------------------------------')
            for line in dense_summary:
                print(line)
            print('======================================================')

        # output layer
        y_ = dense_layers[-1]

        # add an optimizer
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate,name = "optimizer").minimize(cross_entropy)

        # define an accuracy assessment operation
        predict = tf.argmax(y_, 1, name="predict")
        correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1), name="correct_prediction")
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32),name="accuracy")

        # setup the initialisation operator
        init_op = tf.global_variables_initializer()

        # setup recording variables
        # add a summary to store the accuracy
        tf.summary.scalar('accuracy', accuracy)
        merged = tf.summary.merge_all()

        writer = tf.summary.FileWriter('summaries')
        saver = tf.train.Saver()

        tf_nodes = {'x': x,
                'y':y,            
                'cost_function': cross_entropy,
                'optimizer': optimizer,
                'predict': predict,
                'correct_prediction': correct_prediction,
                'accuracy': accuracy,
                'init_op': init_op,
                'merged': merged,
                'writer': writer,
                'saver': saver,
                'keep_prob': keep_prob,
                'learning_rate': learning_rate,
                'class_weights': y_,
                }

        self.set_tf_nodes(tf_nodes)

        return tf_nodes
        
    def _create_new_conv_layer(self, input_data, num_input_channels, num_filters, filter_shape, pool_shape, name):
        """Create a convolutional layer.

            Args:
                input_data: tensorflow tensor
                    The input nodes for the convolutional layer
                num_input_channels: int
                    The number of input channels in input image
                num_filters: int
                    Number of filters to be used in the convolution
                filter_shape: list (int)
                    List of integers defining the shape of the filters.
                    Example: [2,8]
                pool_shape: list (int)
                    List of integers defining the shape of the pooling window.
                    Example: [2,8]
                name: str
                    Name by which the layer will be identified in the graph.

            Returns:
                out_layer: tensorflow layer
                    The convolutional layer.

        """
        # setup the filter input shape for tf.nn.conv_2d
        conv_filt_shape = [filter_shape[0], filter_shape[1], num_input_channels, num_filters]

        # initialise weights and bias for the filter
        weights = tf.Variable(tf.truncated_normal(conv_filt_shape, stddev=0.03), name=name+'_W')
        bias = tf.Variable(tf.truncated_normal([num_filters]), name=name+'_b')

        # setup the convolutional layer operation
        out_layer = tf.nn.conv2d(input_data, weights, [1, 1, 1, 1], padding='SAME')

        # add the bias
        out_layer += bias

        # apply a ReLU non-linear activation
        out_layer = tf.nn.relu(out_layer)

        # now perform max pooling
        # ksize is the argument which defines the size of the max pooling window (i.e. the area over which the maximum is
        # calculated).  It must be 4D to match the convolution - in this case, for each image we want to use a 2 x 2 area
        # applied to each channel
        ksize = [1, pool_shape[0], pool_shape[1], 1]
        # strides defines how the max pooling area moves through the image - a stride of 2 in the x direction will lead to
        # max pooling areas starting at x=0, x=2, x=4 etc. through your image.  If the stride is 1, we will get max pooling
        # overlapping previous max pooling areas (and no reduction in the number of parameters).  In this case, we want
        # to do strides of 2 in the x and y directions.
        strides = [1, 2, 2, 1]
        out_layer = tf.nn.max_pool(out_layer, ksize=ksize, strides=strides, padding='SAME')

        return out_layer

    def _image_shape(self):
        """ Get the shape of the input data.

            Returns:
                img_shape: tuple
                    Shape of the input data images

        """
        tr = self.images[DataUse.TRAINING]

        if tr is None:
            img_shape = self.image_shape

        else:        

            img_shape = get_image_size(tr) 
            self.image_shape = img_shape

            if self.images[DataUse.VALIDATION] is not None:
                assert img_shape == get_image_size(self.images[DataUse.VALIDATION]), "Training and validation images must have same shape."

            if self.images[DataUse.TEST] is not None:
                assert img_shape == get_image_size(self.images[DataUse.TEST]), "Training and test images must have same shape."

        return img_shape

    def train(self, train_batch_gen=None,  batch_size=None, num_epochs=None, learning_rate=None, keep_prob=None, val_acc_goal=1.01):
        """ Train the neural network on the training set.

            Train on the batches of training data provided by the generator ``train_batch_gen``. 

            If a generator is not provided, train on the data stored in the ``images``
            attribute, dividing these data into batches of size ``batch_size``.

            Once training is done, check the accuracy on the validation set.
            
            Record summary statics during training. 


            Args:
                train_batch_gen:
                    A generator that provides (X,Y) tuples, whereeach tuple is
                    a batch of training data (X) and the corresponding labels (Y).
                batch_size: int
                    Batch size. Overwrites batch size specified at initialization.
                num_epochs: int
                    Number of epochs: Overwrites number of epochs specified at initialization.
                learning_rate: float
                    The learning rate to be using by the optimization algorithm
                keep_prob: float
                    Float in the range [0,1] specifying the probability of keeping the weights, 
                    i.e., drop-out will be applied if keep_prob < 1.
                val_acc_goal: float 
                    Terminate training when validation accuracy reaches this value 

            Returns:
                avg_cost: float
                    Average cost of last completed training epoch.
                val_acc: float
                    Accuracy on validation data. Will be 0 if no validation data is provided.

            Example:

                >>> # initialize BasicCNN for classifying 2x2 images
                >>> from ketos.neural_networks.cnn import BasicCNN
                >>> cnn = BasicCNN(image_shape=(2,2), verbosity=0, seed=1)
                >>> # create a small network with one convolutional layers and one dense layer
                >>> params = ConvParams(name='conv_1', n_filters=4, filter_shape=[2,2])
                >>> _ = cnn.create(conv_params=[params], dense_size=[4])
                >>> # give the network some training data
                >>> img0 = np.zeros(shape=(2,2))
                >>> img1 = np.ones(shape=(2,2))
                >>> x = [img0, img1, img0, img1, img0] # input data
                >>> y = [0, 1, 0, 1, 0] # labels
                >>> cnn.set_training_data(x, y)
                >>> cost, _ = cnn.train(batch_size=2, num_epochs=7, learning_rate=0.005)
        """
        if batch_size is None:
            batch_size = self.batch_size
        if num_epochs is None:
            num_epochs = self.num_epochs
        if keep_prob is None:
            keep_prob = self.keep_prob_value
        if learning_rate is None:
            learning_rate = self.learning_rate_value

        sess = self.sess

        x, y = self.get_training_data()
        x_val, y_val = self.get_validation_data()

        y = self._ensure1hot(y)
        y_val = self._ensure1hot(y_val)

        self.writer.add_graph(sess.graph)

        if self.verbosity >= 2:
            if self.epoch_counter == 0: 
                print("\nTraining  started")
            header = '\nEpoch  Cost  Train acc.  Val acc.'
            line   = '----------------------------------'
            print(header)
            print(line)

        # initialise the variables
        if self.epoch_counter == 0:
            sess.run(self.init_op)

       
        if train_batch_gen is not None:
            batches = train_batch_gen.n_batches
        else:
            batches = int(y.shape[0] / batch_size)
        for epoch in range(num_epochs):
            avg_cost = 0
            avg_acc = 0
            val_acc = 0
            for i in range(batches):
                if train_batch_gen is None:
                    offset = i * batch_size
                    x_i = x[offset:(offset + batch_size), :, :, :]
                   
                    y_i = y[offset:(offset + batch_size)]
                else:
                    x_i, y_i = next(train_batch_gen)
                x_i = self._reshape_x(x_i)
                fetch = [self.optimizer, self.cost_function, self.accuracy]

                _, c, a = sess.run(fetches=fetch, feed_dict={self.x: x_i, self.y: y_i, self.learning_rate: learning_rate, self.keep_prob: keep_prob})
                
                avg_cost += c / batches
                avg_acc += a / batches

            val_acc = self.accuracy_on_validation()

            if val_acc >= val_acc_goal:
                break

            if self.verbosity >= 2:
                s = ' {0}/{4}  {1:.3f}  {2:.3f}  {3:.3f}'.format(epoch + 1, avg_cost, avg_acc, val_acc, num_epochs)
                print(s)

            summary = self._get_summary(x=x_val, y=y_val)
            if summary is not None:
                self.writer.add_summary(summary, self.epoch_counter)

            self.epoch_counter += 1

        if self.verbosity >= 2:
            print(line)

        return avg_cost, val_acc

    def train_active(self, provider, iterations=1, batch_size=None, num_epochs=None, learning_rate=None, keep_prob=None, val_acc_goal=1.01):
        """ Train the neural network in an active manner using a data provider module.

            Args:
                provider: ActiveLearningBatchGenerator
                    ActiveLearningBatchGenerator
                iterations: int
                    Number of training iterations.
                batch_size: int
                    Batch size. Overwrites batch size specified at initialization.
                num_epochs: int
                    Number of epochs: Overwrites number of epochs specified at initialization.
                learning_rate: float
                    The learning rate to be using by the optimization algorithm
                keep_prob: float
                    Float in the range [0,1] specifying the probability of keeping the weights, 
                    i.e., drop-out will be applied if keep_prob < 1.
                val_acc_goal: float 
                    Terminate training when validation accuracy reaches this value 

            Returns:
                avg_cost: float
                    Average cost of last completed training epoch.
                val_acc: float
                    Accuracy on validation data. Will be 0 if no validation data is provided.

            Example:

                >>> # initialize BasicCNN for classifying 2x2 images
                >>> from ketos.neural_networks.cnn import BasicCNN
                >>> cnn = BasicCNN(image_shape=(2,2), verbosity=0, seed=1)
                >>> # create a small network with one convolutional layers and one dense layer
                >>> params = ConvParams(name='conv_1', n_filters=4, filter_shape=[2,2])
                >>> _ = cnn.create(conv_params=[params], dense_size=[4])
                >>> # create some training data
                >>> img0 = np.zeros(shape=(2,2))
                >>> img1 = np.ones(shape=(2,2))
                >>> x = [img0, img1, img0, img1, img0, img1, img0] # input data
                >>> y = [0, 1, 0, 1, 0, 1, 0] # labels
                >>> # create a data provider
                >>> from ketos.data_handling.data_feeding import ActiveLearningBatchGenerator
                >>> g = ActiveLearningBatchGenerator(x, y)
                >>> cost, _ = cnn.train_active(provider=g, iterations=3, batch_size=2, num_epochs=7, learning_rate=0.005)
        """    
        for i in range(iterations):

            # get data from provider
            x_train, y_train, keep_frac = provider.get_samples()    

            if self.verbosity >= 2:
                print('\nIteration: {0}/{1}'.format(i+1, iterations))
                print('Keep frac: {0:.1f}%'.format(100.*keep_frac))

            # feed data to neural net
            self.set_training_data(x=x_train, y=to1hot(y_train,2))

            # train
            avg_cost, val_acc = self.train(batch_size=batch_size, num_epochs=num_epochs, learning_rate=learning_rate, keep_prob=keep_prob, val_acc_goal=val_acc_goal)

            # update predictions and confidences
            w = self.get_class_weights(x_train)
            pred = predictions(w)
            conf = class_confidences(w)
            provider.update_prediction_confidence(pred=pred, conf=conf)

            if val_acc >= val_acc_goal:
                break

        return avg_cost, val_acc

    def save(self, destination):
        """ Save the model

            Args:
                destination: str
                    Path to the file in which the model will be saved. 

            Returns:
                None.
        """
        self.saver.save(self.sess, destination)

    def _get_summary(self, x, y):
        """ Obtain summary of model performance on dataset x, y

            Obs: If the dataset contains more than max_frames samples, only the first 
            max_frames samples will be computed.

            Args:
                x: tensor
                    Tensor containing the input data
                y: tensor
                    Tensor containing the labels

            Returns:
                summary
        """

        if x is None:
            return None

        x = self._reshape_x(x)

        N = min(x.shape[0], self.max_frames)
        x = x[:N]
        y = y[:N]

        summary = self.sess.run(fetches=self.merged, feed_dict={self.x: x, self.y: y, self.learning_rate: self.learning_rate_value, self.keep_prob: 1.0})

        return summary

    def _check_accuracy(self, x, y):
        """ Check accuracy of the model by checking how close
            to y the models predictions are when fed x

            Based on the accuracy operation stored in the attribute 'self.accuracy'),
            which is defined by the 'create_net_structure()' method.

            Args:
                x: tensor
                    Tensor containing the input data
                y: tensor
                    Tensor containing the labels

            Returns:
                results: float
                    The accuracy value
        """
        if x is None:
            return 0

        x = self._reshape_x(x) 
        y1hot = self._ensure1hot(y)       
        results = self.sess.run(fetches=self.accuracy, feed_dict={self.x:x, self.y:y1hot, self.learning_rate: self.learning_rate_value, self.keep_prob:1.0})
        return results

    def get_predictions(self, x):
        """ Predict labels by running the model on x

            Args:
                x: tensor
                    Tensor containing the input data.
                
            Returns:
                results: vector
                    A vector containing the predicted labels.                

            Example:

                >>> # initialize BasicCNN for binary classification of 2x2 images
                >>> from ketos.neural_networks.cnn import BasicCNN
                >>> cnn = BasicCNN(image_shape=(2,2), verbosity=0, seed=1, num_labels=2)
                >>> # create a small network with one convolutional layers and one dense layer
                >>> params = ConvParams(name='conv_1', n_filters=4, filter_shape=[2,2])
                >>> _ = cnn.create(conv_params=[params], dense_size=[4])
                >>> # create a 2x2 image
                >>> img = np.zeros(shape=(2,2))
                >>> # obtain the label predicted by the untrained network 
                >>> p = cnn.get_predictions(img)
        """
        x = self._reshape_x(x)

        x, _ = self._split(x)
        results = list()
        for xi in x:
            r = self.sess.run(fetches=self.predict, feed_dict={self.x:xi, self.learning_rate: self.learning_rate_value, self.keep_prob:1.0})
            results = results + r.tolist()

        results = np.array(results)
        return results

    def get_features(self, x, layer_name):
        """ Compute feature vector by running the model on x

            Args:
                x: tensor
                    Tensor containing the input data.
                layer_name: str
                    Name of the feature layer.
                
            Returns:
                results: vector
                    A vector containing the feature values.                
        """
        x = self._reshape_x(x)

        graph = tf.get_default_graph()
        f = graph.get_tensor_by_name("{0}:0".format(layer_name)) 

        x, _ = self._split(x)
        results = list()
        for xi in x:
            r = self.sess.run(fetches=f, feed_dict={self.x:xi, self.learning_rate: self.learning_rate_value, self.keep_prob:1.0})
            results = results + r.tolist()

        results = np.array(results)
        return results

    def get_class_weights(self, x):
        """ Compute classification weights by running the model on x.

            Args:
                x:tensor
                    Tensor containing the input data.
                
            Returns:
                results: vector
                    A vector containing the classification weights. 
        """
        x = self._reshape_x(x)

        fetch = self.class_weights

        x, _ = self._split(x)
        results = list()
        for xi in x:
            feed = {self.x:xi, self.learning_rate: self.learning_rate_value, self.keep_prob:1.0}
            r = self.sess.run(fetches=fetch, feed_dict=feed)
            results = results + r.tolist()

        results = np.array(results)
        return results

    def _reshape_x(self, x):
        """ Reshape input data from a 2d matrix to a 1d vector.

            Args:
                x: numpy array
                    2d array containing the input data.
            
            Returns:
                results: vector
                    A vector containing the flattened inputs.                
        """
        img_shape = self._image_shape()
        reshaped_x = np.reshape(x, (-1, img_shape[0] * img_shape[1]))
        return reshaped_x

    def predict_on_validation(self):
        """ Predict labels by running the model on the validation set.
        
            Returns:
                results: vector
                    A vector containing the predicted labels.                
        """
        x = self.images[DataUse.VALIDATION]
        results = self.get_predictions(x)
        return results

    def predict_on_test(self):
        """ Predict labels by running the model on the test set.
        
            Returns:
                results: vector
                    A vector containing the predicted labels.                
        """
        x = self.images[DataUse.TEST]
        results = self.get_predictions(x)
        return results
    
    def _get_mislabelled(self, x, y, print_report=False, print_detailed_report=False):
        """ Report the number of examples mislabelled by the model.

            Args:
                x:tensor
                    Tensor containing the input data.
                y: tensor
                    Tensor containing the one hot encoded labels.
                print_report: bool
                    If True, prints the percentage of correct and incorrect
                print_detailed_report: bool
                    If True, additionally prints all misclassified examples with the
                    correct and predicted labels.

            Returns:
                results: tuple (numpy arrays)
                    Tuple with two DataFrames (report, incorrect). The first contains
                    number and percentage of correct/incorrect classification. The second,
                    the incorrect examples indices with incorrect and correct labels. 
        
        """
        y1hot = self._ensure1hot(y) 

        x_reshaped = self._reshape_x(x)
        predicted = self.get_predictions(x_reshaped)
        pred_df = pd.DataFrame({"label":np.array(list(map(from1hot,y1hot))), "pred": predicted})
       
        n_predictions = len(pred_df)
        n_correct = sum(pred_df.label == pred_df.pred)
        perc_correct = round(n_correct/n_predictions * 100, 2)
        incorrect = pred_df[pred_df.label != pred_df.pred]
        n_incorrect = len(incorrect)  
        perc_incorrect = round(n_incorrect/n_predictions * 100, 2)
        
        #pred_df.to_csv("predictions.csv")
        report = pd.DataFrame({"correct":[n_correct], "incorrect":[n_incorrect],
                            "%correct":[perc_correct],"%incorrect":[perc_incorrect],
                            "total":[n_predictions]})

        if print_report or print_detailed_report:
            print("=============================================")
            print("Correct classifications: {0} of {1} ({2}%)".format(n_correct, n_predictions, perc_correct))
            print("Incorrect classifications: {0} of {1} ({2})%".format(n_incorrect, n_predictions, perc_incorrect))
            if print_detailed_report:
                print("These were the incorrect classifications:")
                print(incorrect)
            print("=============================================") 
        
        results =(report, incorrect)    
        return results

    def mislabelled_on_validation(self, print_report=False, print_detailed_report=False):
        """ Report the number of examples mislabelled by the trained model on
            the validation set.

            This method wraps around the '_get_mislabelled()' method in the same class.

            Args:
                print_report: bool
                    If True, prints the percentage of correct and incorrect
                print_detailed_report: bool
                    If True, additionally prints all misclassified examples with the
                    correct and predicted labels.
            Returns:
                results: tuple (numpy arrays)
                Tuple with two  DataFrames. The first contains
                number and percentage of correct/incorrect classification. The second,
                the incorrect examples indices with incorrect and correct labels. 
        """
        x = self.images[DataUse.VALIDATION]
        y = self.labels[DataUse.VALIDATION]
        results = self._get_mislabelled(x=x, y=y, print_report=print_report, print_detailed_report=print_detailed_report)
        return results

    def mislabelled_on_test(self, print_report=False, print_detailed_report=False):
        """ Report the number of examples mislabelled by the trained model on
            the test set.

            This method wraps around the '_get_mislabelled()' method in the same class.

            Args:
                print_report: bool
                    If True, prints the percentage of correct and incorrect
                print_detailed_report: bool
                    If True, additionally prints all misclassified examples with the
                    correct and predicted labels.
            Returns:
                results: tuple (numpy arrays)
                Tuple with two  DataFrames. The first contains
                number and percentage of correct/incorrect classification. The second,
                the incorrect examples indices with incorrect and correct labels. 
        """
        x = self.images[DataUse.TEST]
        y = self.labels[DataUse.TEST]
        results = self._get_mislabelled(x=x,y=y, print_report=print_report, print_detailed_report=print_detailed_report)
        return results

    def accuracy_on_train(self):
        """ Report the model accuracy on the training set

            This method wraps around '_check_accuracy()' in the same class.

            Returns:
                results: float
                    The accuracy on the training set.
        """
        x = self.images[DataUse.TRAINING]
        y = self.labels[DataUse.TRAINING]
        results = self._check_accuracy(x,y)
        return results

    def accuracy_on_validation(self):
        """Report the model accuracy on the validation set

            This method wraps around '_check_accuracy()' in the same class.

            Returns:
                results: float
                    The accuracy on the validation set.
        """
        x = self.images[DataUse.VALIDATION]
        y = self.labels[DataUse.VALIDATION]
        results = self._check_accuracy(x, y)
        return results

    def accuracy_on_test(self):
        """Report the model accuracy on the test set

            This method wraps around '_check_accuracy()' in the same class.

            Returns:
                results: float
                    The accuracy on the test set.
        """
        x = self.images[DataUse.TEST]
        y = self.labels[DataUse.TEST]
        results = self._check_accuracy(x,y)
        return results

    def _split(self, x, y=None):
        """ Splits the data into chunks 

            Useful when apply tensorflow operations to large amounts of data

            Args:
                x: tensor
                    Tensor containing the input data
                y: tensor
                    Tensor containing the labels

            Returns:
                x_split: list
                    Input data split up into chunks
                y_split: list
                    Labels split up into chunks
        """

        x_split, y_split = list(), list()

        if x.shape[0] == 0:
            return x_split, y_split

        N = self.max_frames

        imax = int(np.ceil(x.shape[0] / N))
        for i in range(imax):
            i1 = int(N * i)
            i2 = int(min(i1 + N, x.shape[0]))
            xi = x[i1:i2]
            x_split.append(xi)
            if y is not None:
                yi = y[i1:i2]
                y_split.append(yi)

        return x_split, y_split

