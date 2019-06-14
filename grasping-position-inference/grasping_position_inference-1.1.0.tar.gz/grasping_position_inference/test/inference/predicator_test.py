from grasping_position_inference.inference.predicator import Predicator

DUMMY_FILENAME = 'cup.n.01,BACK,BOTTOM,pr2_left_arm,RIGHT-SIDE,-0.5;0.5,-0.8;-0.5,.model'



def test_should_return_valid_x_y_range():
    predicator = Predicator(DUMMY_FILENAME)

    assert predicator._min_x == -0.5
    assert predicator._max_x == 0.5
    assert predicator._min_y == -0.8
    assert predicator._max_y == -0.5