import unittest

from datasets.dssm.ns_generator import NegativeSamplesGenerator
from datasets.utils import data_dir_utils as utils


class NegativeSamplesGeneratorTest(unittest.TestCase):

    def testNegativeSamplesGenerator(self):
        g = NegativeSamplesGenerator(num_neg_samples=10)
        input_files = [utils.get_data_file('dssm.query.doc.pos.txt')]
        output_dir = utils.get_data_dir()
        output_files = g.generate(input_files, output_dir)
        print(output_files)


if __name__ == '__main__':
    unittest.main()
