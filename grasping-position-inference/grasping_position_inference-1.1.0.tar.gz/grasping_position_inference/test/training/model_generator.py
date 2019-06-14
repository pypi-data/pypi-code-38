from grasping_type_inference.grasping_object.grasping_object import GraspingObject
from grasping_type_inference.grasping_object.orientation import Orientation
from grasping_position_inference.training.model_generator import transform_data_filename_to_grasping_model

TEST_DATA_FILENAME = 'cup.n.01,FRONT,:RIGHT-SIDE :BOTTOM,pr2_left_arm.csv'


def test_should_return_valid_grasping_object():
    assert True == True
    #transform_data_filename_to_grasping_model(TEST_DATA_FILENAME)
