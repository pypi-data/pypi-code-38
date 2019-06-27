##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017  SensiML Corporation.                                      #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################


import pandas as pd
from os.path import dirname
from os.path import join
import numpy as np


class ClassLabelException(Exception):
    pass


class DataSets():
    def __init__(self):
        pass

    def load_activity_raw(self):
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, 'data', 'activity_raw.csv'))

    def load_activity_raw_toy(self):
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, 'data', 'activity_raw_toy.csv'))

    def load_activity_norm(self):
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, 'data', 'activity_norm.csv'))

    def load_activity_quant(self):
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, 'data', 'activity_quant.csv'))

    def load_activity_quant_toy(self):
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, 'data', 'activity_quant_toy.csv'))

    def load_gesture_raw(self):
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, 'data', 'gesture_raw.csv'))

    def load_toy_data(self):
        module_path = dirname(__file__)
        return pd.read_csv(join(module_path, 'data', 'toy_data.csv'))

    @staticmethod
    def generate_step_data(window_size=100, num_classes=5, num_iterations=2, scale_factor=100, noise_scale=5, class_labels=None, class_values=None):
        """Generate a labeled test data vector.

        Args:
            window_size (int, optional): The size of each segment window.
            num_classes (int, optional): The number of separate classes
            num_iterations (int, optional): The number of iterations to create.
            scale_factor (int, optional): scale the values of the data by this much before adding noise
            noise_scale (int, optional): The range of noise to add (-noise_scale:noise_scale)
            class_labels (None, optional): you can pass specific class labels as an array, otherwise defaults to
             the range(num_classes)

        Returns:
            DataFrame: a test data vector for building and testing models
        """
        class_labels = check_class_label(num_classes, class_labels)
        class_values = check_class_values(num_classes, class_values)
        delta = window_size*num_classes
        signal_length = num_iterations*delta

        y = np.zeros(signal_length)
        y_label = np.zeros(signal_length)

        for j in range(num_iterations):
            y_temp = np.zeros(window_size*num_classes)
            if j % 2 == 0:
                for i in range(num_classes):

                    y_temp[window_size*i:window_size*(i+1)] = class_values[i]
                    y_label[window_size*i+j*delta:window_size *
                            (i+1)+j*delta] = class_labels[i]
            else:
                for i in range(num_classes):
                    y_temp[window_size*i:window_size *
                           (i+1)] = class_values[-1-i]
                    y_label[window_size*i+j*delta:window_size *
                            (i+1)+j*delta] = class_labels[num_classes-1-i]
            y[delta*j:delta*(j+1)] = y_temp*scale_factor

        if noise_scale > 0:
            y += np.array([np.random.choice(range(-noise_scale, noise_scale))
                           for i in range(len(y))])

        return pd.DataFrame({'Data': y.astype(np.int16), 'Label': y_label.astype(int)})

    @staticmethod
    def generate_harmonic_data(window_size=100, num_classes=5, num_iterations=2, scale_factor=100, noise_scale=5, class_labels=None, harmonic_nodes=None):
        """Generate a labeled test data sin vector.

        Args:
            window_size (int, optional): The size of each segment window.
            num_classes (int, optional): The number of separate classes
            num_iterations (int, optional): The number of iterations to create.
            scale_factor (int, optional): scale the values of the data by this much before adding noise
            noise_scale (int, optional): The range of noise to add (-noise_scale:noise_scale)
            class_labels (None, optional): you can pass specific class labels as an array, otherwise defaults to
             the range(num_classes)

        Returns:
            DataFrame: a test data vector for building and testing models
        """

        class_labels = check_class_label(num_classes, class_labels)
        harmonic_nodes = check_class_values(num_classes, harmonic_nodes)

        delta = window_size*num_classes
        signal_length = num_iterations*delta

        y = np.zeros(signal_length)
        x = np.arange(signal_length)

        y_label = np.zeros(signal_length)
        for j in range(num_iterations):
            y_temp = np.zeros(delta)
            x = np.arange(window_size)
            if j % 2 == 0:
                for i in range(num_classes):
                    y_temp[window_size*i:window_size *
                           (i+1)] = get_standing_wave(x, window_size, harmonic_nodes[i])
                    y_label[window_size*i+j*delta:window_size *
                            (i+1)+j*delta] = class_labels[i]
            else:
                for i in range(num_classes):
                    y_temp[window_size*i:window_size *
                           (i+1)] = get_standing_wave(x, window_size, harmonic_nodes[-1-i])
                    y_label[window_size*i+j*delta:window_size *
                            (i+1)+j*delta] = class_labels[num_classes-1-i]
            y[delta*j:delta*(j+1)] = y_temp*scale_factor

        if noise_scale > 0:
            y += np.array([np.random.choice(range(-noise_scale, noise_scale))
                           for i in range(len(y))])

        return pd.DataFrame({'Data': y.astype(np.int16), 'Label': y_label.astype(int)})


def get_standing_wave(x, L, n):
    ld = 2. * L / n
    return np.sin(x*(2*np.pi) / ld)


def check_class_label(num_classes, class_labels=None):
    if class_labels is None:
        class_labels = range(1, num_classes+1)
    elif len(class_labels) != num_classes:
        raise ClassLabelException(
            "The number of classes is not equal to the number of class labels.")

    for i in class_labels:
        if type(i) != type(1):
            raise ClassLabelException("class labels must be integers.")
    if i <= 0:
        raise ClassLabelException("class labels must be greater than zero.")

    return class_labels


def check_class_values(num_classes, class_values=None):
    if class_values is None:
        class_values = range(1, num_classes+1)
    elif len(class_values) != num_classes:
        raise ClassLabelException(
            "The number of classes is not equal to the number of class values.")

    for i in class_values:
        if type(i) != type(1):
            raise ClassLabelException("class values must be type int")
        if i <= 0:
            raise ClassLabelException(
                "class values must be greater than zero.")

    return class_values
