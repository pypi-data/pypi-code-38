# encoding: UTF-8

import os
import unittest
from ptcaffe.utils.prototxt import parse_prototxt
from ptcaffe.utils.parser import parse_prototxt as parse_prototxt_new


class TestParser(unittest.TestCase):
    def test_compatibility(self):
        # collect all `.prototxt` files in `examples/`
        here = os.path.dirname(os.path.abspath(__file__))
        test_files = []
        for dirname, _, files in os.walk(os.path.join(here, '..', '..', 'examples')):
            for file in files:
                if file.endswith('.prototxt'):
                    test_files.append(os.path.join(dirname, file))

        for filename in test_files:
            reference = parse_prototxt(filename)
            result = parse_prototxt_new(filename)

            self.assertEqual(result, reference)
