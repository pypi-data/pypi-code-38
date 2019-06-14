from os.path import join
import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib
from grasping_position_inference.root import ABSOLUTE_PATH

from grasping_position_inference.training.exceptions import DataSetIsEmpty, ModelIsNotTrained

MODEL_PATH = join(ABSOLUTE_PATH, 'models')


def _remove_negative_zero(number):
    if number == 0.0:
        return 0.0
    else:
        return number


class Model(object):
    def __init__(self, data_filename, data_path, model_path):
        self._data_path = data_path
        self._model_path = model_path
        self.data_filename = data_filename
        self.grasping_object_type, self.grasping_type, self.robot_face, self.bottom_face, self.arm \
            = self._parse_data_filename()
        self._data = self._read_data()
        self._min_x, self._min_y, self._max_x, self._max_y = self._determine_feature_space()

        self._trained_model = None

    def _determine_feature_space(self):
        min_x, min_y = self._data[['t_x', 't_y']].min()
        max_x, max_y = self._data[['t_x', 't_y']].max()

        min_x, min_y, max_x, max_y = round(min_x, 1), round(min_y, 1), round(max_x, 1), round(max_y, 1)

        if min_x == 0.0:
            min_x = 0.0

        return _remove_negative_zero(min_x), \
               _remove_negative_zero(min_y), \
               _remove_negative_zero(max_x), \
               _remove_negative_zero(max_y)

    def _parse_data_filename(self):
        grasping_object_type, grasping_type, faces, arm = self.data_filename.split(',')
        arm = arm.split('.')[0]
        robot_face, bottom_face = faces.split()
        robot_face = robot_face.replace(':', '')
        bottom_face = bottom_face.replace(':', '')

        return grasping_object_type, grasping_type, robot_face, bottom_face, arm

    def _read_data(self):
        data_filepath = join(self._data_path, self.data_filename)
        return pd.read_csv(data_filepath, sep=',')

    def train(self):
        if self._data.empty:
            error_message = 'The empty data set "{}" cannot be used for training.'.format(self.data_filename)
            raise DataSetIsEmpty(error_message)

        features = self._data[['t_x', 't_y']]
        labels = self._data["success"].map(lambda x: 1 if x else 0)

        gnb = GaussianNB()

        self._trained_model = gnb.fit(features, labels)

    def store(self):
        if self._trained_model is None:
            error_message = 'The model has to be trained before it can be stored.'
            raise ModelIsNotTrained(error_message)

        model_name = '{},{},{},{},{},{};{},{};{},.model'.format(
                                                    self.grasping_object_type,
                                                    self.grasping_type,
                                                    self.bottom_face,
                                                    self.arm,
                                                    self.robot_face,
                                                    self._min_x,
                                                    self._max_x,
                                                    self._min_y,
                                                    self._max_y)
        model_save_path = join(self._model_path, model_name)
        joblib.dump(self._trained_model, model_save_path)
