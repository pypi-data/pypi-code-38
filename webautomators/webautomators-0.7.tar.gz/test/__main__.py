import unittest
import HtmlTestRunner


if  __name__ == "__main__":
    #from instances_test import * 
    from drivers_test import *
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='htmlcov'))
