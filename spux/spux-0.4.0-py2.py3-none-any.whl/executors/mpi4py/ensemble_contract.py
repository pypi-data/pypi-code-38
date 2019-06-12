# # # # # # # # # # # # # # # # # # # # # # # # # #
# Contract routine for the Mpi4pyEnsemble class
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

from .ensemble_resample import resample

def universe_address ():

    address = MPI.COMM_WORLD.Get_rank ()
    return address

INIT = b'<init>'
CALL = b'<call>'
RESA = b'<resa>'
DONE = b'<done>'
EXIT = b'<exit>'
NONE = bytearray ('<none>', 'utf8')

class Instruction (object):
    """Class to consistently pack instructions."""

    def __init__ (self, key, value=None):

        self.key = key
        self.value = value

    @property
    def list (self):

        return [self.key, len (self.key), MPI.CHAR]

# worker thread
def contract (manager, peers):
    """Define the steps to execute a set of instructions for an Ensemble task."""

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

            # construct timing
            timing = Timing ()

            # get bcast ensemble
            ensemble = manager.bcast (None)

            # bind ensemble
            ensemble.root = taskroot

            # bind ensemble task
            ensemble.task.root = taskroot

            # bind ensemble task executor
            if hasattr (ensemble.task, 'executor'):
                ensemble.task.executor.bind (taskroot, taskport)

            # get scattered ensemble tasks 'indices'
            timing.start ('scatter tasks')
            indices = manager.scatter (None)
            timing.time ("scatter tasks")

            # initialize ensemble tasks
            timing.start ('init')
            ensemble.init (indices)
            timing.time ('init')

            # time init sync overhead
            timing.start ('init sync')
            manager.Barrier ()
            timing.time ('init sync')

        while True:

            # receive instruction
            timing.start ('instruction')
            instruction = Instruction (NONE)
            manager.Bcast (instruction.list)
            timing.time ('instruction')

            if instruction.key == CALL:
                task = manager.bcast (None)
                method = task ['method']
                args = task ['args']
                results = task ['results']
                timing.start (method)
                call = getattr (ensemble, method)
                result = call (*args)
                timing.time (method)
                timing.start (method + ' sync')
                peers.Barrier ()
                timing.time (method + ' sync')

                if results:
                    timing.start (method + ' gather')
                    manager.gather (result)
                    timing.time (method + ' gather')

            elif instruction.key == RESA:

                # get scattered ensemble tasks 'routing'
                timing.start ('scatter routings')
                routing = manager.scatter (None)
                timing.time ('scatter routings')

                # resample (delete and replicate) tasks and balance ensembles according to specified particle 'routing'
                timing.start ('resample')
                timing_resample = resample (ensemble, routing, peers)
                timing.time ('resample')
                timing += timing_resample

                # sync with manager
                timing.start ('resample sync')
                manager.Barrier ()
                timing.time ('resample sync')

            elif instruction.key == DONE:

                # exit ensemble
                ensemble.exit ()

                # gather timings in manager
                manager.gather (timing)

                # disconnect
                manager.Disconnect ()
                break

            else:
                print("Fatal. Instruction key: ",instruction.key," not handled in ensemble_contract. This may be a bug.")
                manager.Abort()
