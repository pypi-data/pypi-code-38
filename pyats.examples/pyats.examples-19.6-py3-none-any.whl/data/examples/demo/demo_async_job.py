'''Demo Async Jobfile

The purpose of this jobfile is to demonstrate how scripts are run as tasks,
and how tasks may be run in parallel, and generate concurrent results.


To run this jobfile in Easypy:

    bash$ pyats run job demo_async_job.py --testbed-file demo_tb_topology.yaml

'''

import os

from pyats.easypy import run, Task

here = os.path.dirname(__file__)

# main() function defines the entry point of each job file
def main():

    # run a single task, wait for it to finish using run() api
    # note that this script requires parameters to be provided
    result = run(testscript = 'demo_steps.py',
                 a = 2, b = 3)

    # do below only if first script passes
    if result:

        # now run two tasks in parallel
        task_1 = Task(testscript = 'demo_results.py')
        task_2 = Task(testscript = 'demo_loops.py')

        # start tasks
        task_1.start()
        task_2.start()

        # wait for tasks to finish
        task_1.wait()
        task_2.wait()
