# # # # # # # # # # # # # # # # # # # # # # # # # #
# Contract routige for the Mpi4pyPool executor class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from mpi4py import MPI
import cloudpickle
MPI.pickle.__init__ (cloudpickle.dumps, cloudpickle.loads)

from ...utils.timing import Timing

def universe_address ():
    """Return rank in MPI COMM_WORLD"""

    address = MPI.COMM_WORLD.Get_rank ()
    return address

INIT = b'<init>'
TASK = b'<task>'
DONE = b'<done>'
EXIT = b'<exit>'
NONE = bytearray ('<none>', 'utf8')

class Instruction (object):
    """Class to consistently pack instructions."""

    def __init__ (self, key, value=None, mode=None):

        self.key = key
        self.value = value
        self.mode = mode

    @property
    def list (self):

        return [self.key, len (self.key), MPI.CHAR]

# worker thread
def contract (manager, peers):
    """Define the steps to execute a set of instructions for a Pool task."""

    # get bcast manager port, task template and connector
    port, template, connector = manager.bcast (None)

    # bind task
    taskroot = template.rootcall (peers)

    # set connector for the task and init task executor
    if hasattr (template, 'executor'):
        template.executor.connector = connector
        taskport = template.executor.init (peers=peers, internal=1)
    else:
        taskport = None

    # disconnect
    manager.Disconnect ()

    # loop for incoming tasks
    while True:

        # connect to manager
        manager = connector.connect (port, peers)

        # receive instruction
        instruction = Instruction (NONE)
        manager.Bcast (instruction.list)

        # exit instruction
        if instruction.key == EXIT:
            if hasattr (template, 'executor'):
                template.executor.exit ()
            manager.Disconnect ()
            break

        # init instruction
        if instruction.key == INIT:

            # receive mode
            mode = bytearray ('NONE', 'utf8')
            manager.Bcast ([mode, 4, MPI.CHAR])

            # setup timing
            timing = Timing ()

            # get bcast func and args
            function, args = manager.bcast (None)

            # bind function if it is pre-specified
            if mode == b'SFMP':
                function.root = taskroot
                if hasattr (function, 'executor'):
                    function.executor.bind (taskroot, taskport)

        while True:

            # receive instruction
            timing.start ('instruction')
            instruction = Instruction (NONE)
            manager.Recv (instruction.list)
            timing.time ('instruction')

            if instruction.key == TASK:
                task = manager.recv ()
                timing.start ('task')
                if mode == b'SFMP':
                    result = function (task, *args)
                if mode == b'MFNP':
                    task.root = taskroot
                    if hasattr (task, 'executor'):
                        task.executor.bind (taskroot, taskport)
                    result = task (*args)
                if mode == b'MFMP':
                    taskfunction = task ['function']
                    taskfunction.root = taskroot
                    if hasattr (taskfunction, 'executor'):
                        taskfunction.executor.bind (taskroot, taskport)
                    result = taskfunction (task ['parameters'], *args)
                timing.time ('task')
                manager.send (result, dest=0)

            elif instruction.key == DONE:
                timing.start ('sync')
                manager.Barrier ()
                timing.time ('sync')
                manager.gather (timing)
                manager.Disconnect ()
                break

            else:
                print("Fatal. Instruction key: ",instruction.key," not handled in pool_contract. This is a bug.")
                manager.Abort ()
