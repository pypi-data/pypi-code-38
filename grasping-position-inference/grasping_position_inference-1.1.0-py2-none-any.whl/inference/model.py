# coding=utf8

from os import listdir

from grasping_position_inference.inference.predicator import Predicator
from grasping_position_inference.inference.probability_grid import ProbabilityGrid


class Model(object):
    def __init__(self, model_path):
        self.predictors = []
        self._model_path = model_path

    def add_predictor(self, *evidences):
        grasping_object_type, grasping_type, robot_face, bottom_face, arm = evidences
        predicator_name = "{},{},{},{},{},".format(grasping_object_type, grasping_type,bottom_face, arm, robot_face)
        models = listdir(self._model_path)
        file_name = ''

        for model in models:
            if model.startswith(predicator_name):
                file_name = model
                break

        if file_name:
            predicator = Predicator(file_name, self._model_path)
            self.predictors.append(predicator)

    def get_probability_distribution_for_grid(self):
        probability_grid = ProbabilityGrid()

        for predictor in self.predictors:
            probability_grid.update(predictor)

        return probability_grid.get_grid()





