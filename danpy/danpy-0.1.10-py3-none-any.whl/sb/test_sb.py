import pytest
from .sb import *

def test_double_input():
  output = double_input(2)
  assert output == 4, "Error with double_input."
