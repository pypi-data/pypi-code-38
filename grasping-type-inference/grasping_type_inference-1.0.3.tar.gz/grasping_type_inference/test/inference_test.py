from grasping_type_inference.inference import Inference


def test_should_return_the_most_probable_result():
    inference = Inference(':LEFT-SIDE', ':BOTTOM', 'cup.n.01')
    result = inference.get_most_probable_result()

    assert 'LEFT-SIDE' == result

    inference = Inference(':LEFT-SIDE', ':BOTTOM', 'bowl.n.01')
    result = inference.get_most_probable_result()

    assert 'TOP' == result

    inference = Inference(':LEFT-SIDE', ':BOTTOM', 'spoon.n.01')
    result = inference.get_most_probable_result()

    assert 'TOP' == result


def test_should_return_probability_distribution():
    inference = Inference(':LEFT-SIDE', ':BOTTOM', 'cup.n.01')
    result = inference.get_storted_list_of_grasping_types_based_on_probability()

    assert list == type(result)

    inference = Inference(':LEFT-SIDE', ':BOTTOM', 'bowl.n.01')
    result = inference.get_storted_list_of_grasping_types_based_on_probability()

    assert list == type(result)

    inference = Inference(':LEFT-SIDE', ':BOTTOM', 'spoon.n.01')
    result = inference.get_storted_list_of_grasping_types_based_on_probability()

    assert list == type(result)