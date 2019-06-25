'''Demo AEtest Features

This AEtest script is intended to demonstrate the following features:
    
    - pdb on failure/error
    - max_failures
    - randomization

Run this jobfile in standalone:
    
    # enable pdb on fail
    bash$ python demo_aetest_features.py -pdb

    # enable randomization
    bash$ python demo_aetest_features.py -random

    # randomization seed replay
    bash$ python demo_aetest_features.py -random -random_seed 100

    # max_failures feature
    bash$ python demo_aetest_features.py -max_failures 0

'''

from pyats import aetest

# define a common setup section
class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def subsection(self, steps):
        pass

# define a single testcase
class FailedTestcase(aetest.Testcase):

    # uncomment the line below to mark the testcase as must-pass
    #must_pass = True

    @aetest.test
    def test(self, steps): 
        with steps.start('step 1') as step:
            self.failed()

# define a single testcase
class ErroredTestcase(aetest.Testcase):

    @aetest.test
    def test(self): 
        callingFuncDoesntExist()

# define a common cleanup section
class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def subsection(self):
        pass

# standalone execution
if __name__ == '__main__':
    aetest.main()