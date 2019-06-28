"""This module is a custom module designed for general use in the Omnis project.
"""
import csv
import os

import cv2
import keras
import numpy as np


class PredictGenerator(keras.utils.Sequence):
    def __init__(self, image_filenames=None, image_classes=None,
                 batch_size=None, image_shape=None, shuffle=False):
        self.image_filenames = image_filenames
        self.image_classes = image_classes
        self.batch_size = batch_size
        self.image_shape = image_shape
        self.shuffle = shuffle
        self.predict_order_filenames = []

    def __len__(self):
        return int(np.ceil(len(self.image_filenames) / float(self.batch_size)))

    def __getitem__(self, idx):
        batch_x = self.image_filenames[
            idx * self.batch_size
            :(idx + 1) * self.batch_size
        ]

        x = []
        for filename in batch_x:
            _, only_file_name = os.path.split(filename)
            self.predict_order_filenames.append(only_file_name)
            img = cv2.imread(filename)
            test_data = np.expand_dims(img, axis=0)
            resized_img = cv2.resize(test_data[0], self.image_shape)
            x.append(resized_img)

        data_array = np.asarray(x)
        data_array = data_array.astype('float32')
        data_array /= 255
        return data_array

    def flow_one_directory(self, directory_path,
                           shuffle=False, batch_size=1, image_shape=None):
        file_list = os.listdir(directory_path)
        self.image_filenames = []
        for file_name in file_list:
            self.image_filenames.append(directory_path + '/' + file_name)
        self.batch_size = batch_size
        self.image_shape = image_shape
        self.shuffle = shuffle

        return self


class TrainGenerator(keras.utils.Sequence):
    def __init__(self, image_filenames=None, image_shape=None, shuffle=False):
        self.image_filenames = image_filenames
        self.image_classes = []
        self.class_indices = []
        self.image_shape = image_shape
        self.shuffle = shuffle

    def __len__(self):
        return int(np.ceil(len(self.image_filenames) / float(self.batch_size)))

    def __getitem__(self, idx):
        batch_x = self.image_filenames[
            idx * self.batch_size
            :(idx + 1) * self.batch_size
        ]
        class_x = self.image_classes[
            idx * self.batch_size
            :(idx + 1) * self.batch_size
        ]

        cnt = 0
        x = []
        index_list = []
        for filename in batch_x:
            try:
                img = cv2.imread(filename)
                resized_img = cv2.resize(img, self.image_shape)
                x.append(resized_img)
                index_list.append(cnt)
                cnt += 1
            except BaseException:
                pass

        batch_y = np.zeros((cnt, len(self.class_indices)), dtype='float')

        i = 0
        for index in index_list:
            find_index = self.class_indices.index(class_x[index])
            batch_y[i, find_index] = 1
            i += 1

        x_array = np.array(x)
        return x_array, batch_y

    def flow_from_csv(self, csv_file_path, image_directory_path,
                      shuffle=False, target_size=None, batch_size=1):
        f = open(csv_file_path, 'r', encoding='utf-8')
        csv_reader = csv.reader(f)
        self.image_classes = list()
        self.image_filenames = list()

        for line in csv_reader:
            atoms = line
            file_full_path = os.path.join(
                image_directory_path, atoms[0] + '.jpg')
            if os.path.isfile(file_full_path):
                self.image_classes.append(atoms[2])
                self.image_filenames.append(file_full_path)
        f.close()
        self.class_indices = list(set(self.image_classes))
        self.shuffle = shuffle
        self.image_shape = target_size
        self.batch_size = batch_size
        self.n = len(self.image_filenames)
        return self
