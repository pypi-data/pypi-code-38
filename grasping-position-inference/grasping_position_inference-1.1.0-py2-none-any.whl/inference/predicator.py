from os.path import join

from sklearn.externals import joblib

from grasping_position_inference.inference.grid import Grid
from grasping_position_inference.root import ABSOLUTE_PATH

MODEL_PATH = join(ABSOLUTE_PATH, 'models')
X_STEP_SIZE = 0.01
Y_STEP_SIZE = 0.01


class Predicator(object):
    def __init__(self, file_name, model_path=MODEL_PATH):
        self._file_name = file_name
        self._model_filepath = join(model_path, file_name)
        self._min_x, self._max_x, self._min_y, self._max_y = self._get_min_max_values_for_x_y()
        self._grid = self._create_grid()

    def _get_min_max_values_for_x_y(self):
        #cup.n.01,BACK,BOTTOM,pr2_left_arm,BACK,-0.8;-0.5,0.0;0.5,.model
        splitted_file_name = self._file_name.split(',')
        x_range, y_range = splitted_file_name[-3], splitted_file_name[-2]
        min_x, max_x = map(float, x_range.split(';'))
        min_y, max_y = map(float, y_range.split(';'))

        return min_x, max_x, min_y, max_y

    def _create_grid(self):
        x_parameters = [self._min_x, self._max_x, X_STEP_SIZE]
        y_parameters = [self._min_y, self._max_y, Y_STEP_SIZE]

        grid = Grid(x_parameters, y_parameters)

        return grid

    def get_probability_distribution_for_grid(self):
        model = joblib.load(self._model_filepath)

        result = []

        for i in range(0, len(self._grid.x)):
            success_rates = []
            features = map(list, zip(self._grid.x[i], self._grid.y[i]))
            for predict_values in model.predict_proba(features):
                success_rate = _get_success_rate(model, predict_values)
                success_rates.append(success_rate)
            result.append(success_rates)

        return result


#Some data sets contain only one type of success. Meaning all try outs failed or were successful
#Therefore the classifier only predicts 1. for success or failed
#This behaviour have to be handled

def _get_success_rate(model, predict_values):
    if len(predict_values) == 2:
        return predict_values[1]
    else:
        success_type = model.classes_[0]
        if success_type == 0:
            return 0.
        else:
            return 1.