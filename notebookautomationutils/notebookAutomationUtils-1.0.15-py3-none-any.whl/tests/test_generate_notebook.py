import os
import unittest
import generate_notebook as nb
from unittest.mock import patch, Mock
from unittest import TestCase

class TestGenerateNotebook(TestCase):
    """
    Tests for generate notebook
    """
    def test_generate_release_notebook(self):
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath1 = filepath[:index]
        dirpath2 = dirpath1 + "/"

        nb.generate_release_notebook()
        expected = dirpath2 + "/Notebook.ipynb"
        assert os.path.exists(expected) == True