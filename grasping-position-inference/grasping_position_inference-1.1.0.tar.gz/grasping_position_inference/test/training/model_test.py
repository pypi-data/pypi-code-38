import pytest

from grasping_position_inference.training.exceptions import DataSetIsEmpty, ModelIsNotTrained
from grasping_position_inference.training.model import Model
import pandas as pd
from mock import patch

DUMMY_FILENAME = 'cup.n.01,BACK,:BACK :BOTTOM,pr2_left_arm.csv'

@patch('grasping_position_inference.training.model.Model._read_data', return_value=pd.DataFrame())
def test_should_throw_data_set_is_empty_exception(mocker):
    model = Model(DUMMY_FILENAME)
    with pytest.raises(DataSetIsEmpty):
        model.train()


@patch('grasping_position_inference.training.model.Model._read_data', return_value=pd.DataFrame())
def test_should_throw_model_is_not_trained(mocker):
    model = Model(DUMMY_FILENAME)
    with pytest.raises(ModelIsNotTrained):
        model.store()



