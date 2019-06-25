'''Demo Execution Groups & Execution UIDs

The goal of this script is to demonstrate how AEtest execution groups are 
assigned to testcases, how testcase IDs work, and and how they can be used to 
control which groups of testcases to run, and which exact testcase to run.

Run this script in standalone:
    
    # run sanity group
    bash$ python demo_groups.py -groups "Or('sanity')"

    # run regression group
    bash$ python demo_groups.py -groups "Or('regression')"

    # run sanity & regression groups
    bash$ python demo_groups.py -groups "Or('sanity', 'regression')"

    # run testcase by uid
    bash$ python demo_groups.py -uids "Or('sanity_testcase')"
'''
from pyats import aetest


class SanityTestcase(aetest.Testcase):

    # assign a unique uid to testcase
    uid = 'sanity_testcase'

    # associate testcases to groups
    groups = ['sanity']

class RegressionTestcase(aetest.Testcase):

    # assign a unique uid to testcase
    uid = 'regression_testcase'

    # associate testcases to groups
    groups = ['regression']


# standalone execution
if __name__ == '__main__':
    aetest.main()