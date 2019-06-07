import os

from grasping_type_inference.learning import train_all_grasping_mlns
from grasping_type_inference.definitions import ROOT_DIR


TRAINING_DATA_FILE_PATH = os.path.join(ROOT_DIR, 'mln')
MLN_DATA_FILE_PATH = os.path.join(ROOT_DIR, 'test', 'mln')


def test_should_train_all_mlns_successful():
    train_all_grasping_mlns(TRAINING_DATA_FILE_PATH)


def test_should_train_all_mlns_successful_with_parameter():
    train_all_grasping_mlns(TRAINING_DATA_FILE_PATH, MLN_DATA_FILE_PATH)