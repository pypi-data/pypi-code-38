import unittest

from grasping_object_test.grasping_object_test_suite import test_suites as grasping_object_test_suites
from markov_logic_network_test.markov_logic_network_test_suite import test_suites as markov_logic_network_test_suite
from word_net_test.word_net_test_suite import WordNetTestSuite

test_suites = grasping_object_test_suites + markov_logic_network_test_suite + [WordNetTestSuite()]

if __name__ == '__main__':
    main_suite = unittest.TestSuite(test_suites)
    runner = unittest.TextTestRunner()
    result = runner.run(main_suite)
