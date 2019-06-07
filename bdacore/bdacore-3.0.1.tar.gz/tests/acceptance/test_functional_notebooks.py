# coding: utf8
import os, io
import pytest
import unittest
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError

pytestmark = pytest.mark.functional


@pytest.mark.functional
class TestFunctional(unittest.TestCase):
    def setUp(self):
        self.basedir = os.path.dirname(os.path.abspath(__file__))

        self.run_path = '{}/tests_notebooks'.format(self.basedir)
        self.output_dir = '{}/out'.format(self.basedir)
        self.notebook_filename_out = '{}/out/TestOutput_{}.ipynb'
        self.notebook_base_url = '{}/tests_notebooks/{}.ipynb'
        self.env_name = os.environ.get('CONDA_DEFAULT_ENV', 'bdacore_py3')  ## get the env name variable from makefile??

        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    def test_tutorial_FE_TimesSeries_execute_whithout_error(self):
        # Given
        notebook_name = 'FE_TimesSeries'

        # When
        self.execute_notebook(notebook_name)

    def test_tutorial_LSH_execute_whithout_error(self):
        # Given
        notebook_name = 'LSH'

        # When
        self.execute_notebook(notebook_name)

    def test_tutorial_NeuralNets_Autoencoder_execute_whithout_error(self):
        # Given
        notebook_name = 'NeuralNets_AutoEncoder'

        # When
        self.execute_notebook(notebook_name)

    def test_tutorial_NeuralNets_TextClassification_execute_whithout_error(self):
        # Given
        notebook_name = 'NeuralNets_TextClassification'

        # When
        self.execute_notebook(notebook_name)

    def test_tutorial_Outliers_Detection_execute_whithout_error(self):
        # Given
        notebook_name = 'Outliers_Detection'

        # When
        self.execute_notebook(notebook_name)

    def test_tutorial_UnsupervisedSequenceMining_execute_whithout_error(self):
        # Given
        notebook_name = 'UnsupervisedSequenceMining'

        # When
        self.execute_notebook(notebook_name)

    def execute_notebook(self, notebook_name):
        with io.open(self.notebook_base_url.format(self.basedir, notebook_name), encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
            ep = ExecutePreprocessor(timeout=1000, kernel_name=self.env_name)

            try:
                out = ep.preprocess(nb, {'metadata': {'path': self.run_path}})
            except CellExecutionError:
                out = None
                msg = 'Error executing the notebook "%s".\n\n' % notebook_name
                msg += 'See notebook "%s" for the traceback.' % self.notebook_filename_out
                print(msg)
                raise
            finally:
                with io.open(self.notebook_filename_out.format(self.basedir, notebook_name), mode='wt',
                             encoding='utf-8') as f:
                    nbformat.write(nb, f)
