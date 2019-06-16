import unittest
import doctest
from fig_html.utils import sample_fig_maker
from fig_html.utils import path
from fig_html import fig_html_maker

modules = [sample_fig_maker, path, fig_html_maker]
suite = unittest.TestSuite()

for module in modules:
    suite.addTest(doctest.DocTestSuite(module))
runner = unittest.TextTestRunner()
runner.run(suite)