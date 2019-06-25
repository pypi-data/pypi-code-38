# To run the job:
# pyats run job $VIRTUAL_ENV/examples/basic/job/basic_example2_job.py

# Description: This example shows how to scripts can be run
#              in pyats. See basic_example.py first.
# This job file execute twice the same testscript. This demonstrate how to
# execute multiple testscript inside the same job file

import os
from pyats.easypy import run

# All run() must be inside a main function
def main():
    # Find the location of the script in relation to the job file
    test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    testscript = os.path.join(test_path, 'basic_example_script.py')
    
    # Execute the first testscript
    run(testscript=testscript)
    # Execute the second testscript
    # It will wait for the first one to be done first
    run(testscript=testscript)
