# # # # # # # # # # # # # # # # # # # # # # # # # #
# Connector class for subdivision of MPI.COMM_WORLD into manager and workers
# using mpi4py bindings and MPI backend for distributed memory paralellization
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from mpi4py import MPI
import sys, socket
from .utils import universe_address

# compute worker ranks for the current level of resources
def get_ranks (resource, root=None, manager=0):
    """Compute worker ranks for the current level of resources"""

    stride = resource ['resources']
    count = resource ['workers']
    ranks = [manager + i * stride for i in range (count)]
    if root is not None:
        offset = 0
        for level in root:
            if level ['address'] is not None:
                offset += 1 + level ['address'] * level ['resources']
        ranks = [offset + rank for rank in ranks]
    return ranks

class Split (object):
    """Class to establish workers MPI processes by using server/client mode through ports."""

    def __init__ (self, verbosity=0):

        self.size = MPI.COMM_WORLD.Get_size ()
        self.rank = universe_address ()
        self.verbosity = verbosity
        self.root = ( self.rank == 0 )

        if verbosity:
            hostnm = 'unknown'
            try:
                hostnm = socket.gethostname()
            except:
                pass
            print("I AM RANK: ",self.rank,"OF: ",self.size, " on host: ", hostnm)
            mpiver = MPI.Get_version()
            print("using MPI version:",mpiver)
            mpilibver = MPI.Get_library_version()
            print("using MPI libversion:",mpilibver)
            self.cwrank = self.rank #handy
            sys.stdout.flush()

    # barrier for pool slots: get resources, split pool accordingly, and wait for incoming tasks
    def barrier (self):
        """Split workers from manager, split workers into pools, wait for tasks."""

        if not self.root:

            # get bcast resources from the pool root
            self.resources = MPI.COMM_WORLD.bcast (None)

            # split away pool root from the pool slots
            self.pool = MPI.COMM_WORLD.Split (self.root)
            self.rank = self.pool.Get_rank ()

            # split pool (recursively) - sets self.peers intra-communicators
            self.split ()

            # barrier for completion
            MPI.COMM_WORLD.Barrier ()

            # wait for port and establish connection
            port = MPI.COMM_WORLD.recv (source=MPI.ANY_SOURCE)
            manager = self.connect (port, self.peers)

            # get contract and work according to it
            contract = manager.bcast (None)
            contract (manager, self.peers)

            # exit once finished
            sys.exit ()

    # initialization for pool root: bcast resources and split away from pool slots
    def init (self, resources):
        """Initialization for manager: bcast resources and split away from pool slots."""

        self.resources = resources

        # manager sends out requests for communicators
        if self.root:

            # bcast resources throughout the pool
            MPI.COMM_WORLD.bcast (self.resources)

            # split away pool root from the pool slots
            MPI.COMM_WORLD.Split (self.root)

            # barrier for completion
            MPI.COMM_WORLD.Barrier ()

    # split pool (recursively)
    def split (self):
        """Split workers recursively into several pools of workers."""

        # if no additional resources are needed, skip the splitting
        if self.resources [0] ['manager'] == 0 and self.resources [0] ['workers'] == 1:
            del self.resources [0]
            if len (self.resources) > 0:
                self.split ()

        # get ranks according to the requested resources
        ranks = get_ranks (self.resources [0])

        # worker ranks form pool intra-communicator
        if self.rank in set (ranks):
            self.peers = self.pool.Split (color=len(ranks))
            self.rank = self.peers.Get_rank ()

            if (self.peers == MPI.COMM_NULL):
                print("Fatal. Exiting split without a self.peers intracomm (1). This is a bug.")
                self.peers.Abort()
                self.pool.Abort()
            return

        # remaining groups of pool slots (inbetween workers) form separate pools
        else:
            if self.resources [0] ['resources'] == 1:
                if (len(self.resources) != 1):
                    self.peers.Abort()
                    self.pool.Abort()
                if (self.peers == MPI.COMM_NULL):
                    print("Fatal. Exiting split without a self.peers intracomm (2). This is a bug.")
                    self.peers.Abort()
                    self.pool.Abort()
                return
            color = self.rank // self.resources [0] ['resources']
            if ( color == len(ranks) ):
                print("Fatal. Color of worker is equal to color of level-managers. This is a bug or you are using too many resources.")
                print(color,len(ranks),ranks,self.rank)
                self.pool.Abort()
            self.pool = self.pool.Split (color)
            self.rank = self.pool.Get_rank ()
            del self.resources [0]

            if len (self.resources) > 0:
                self.split ()
            else:
                if (self.peers == MPI.COMM_NULL):
                    print("Fatal. Exiting split without a self.peers intracomm (3). This is a bug.")
                    self.peers.Abort()
                    self.pool.Abort()
                print("Exiting cause self.resources has length 0: ",self.peers)
                print("rank ",self.rank," getting out with color: ", len(ranks) )
                print("rank ",self.rank," has resources at exit: ",self.resources)
                sys.stdout.flush()

                return

    # connect manager with the number of requested workers by returning a port needed to connect to an inter-communicator
    def bootup (self, contract, task, resource, root, verbosity):
        """Inter-connect manager with the number of requested workers by returning a port."""

        # get ranks according to specified resources
        ranks = get_ranks (resource, root, manager=1)

        # open a port for workers to connect to
        port = MPI.Open_port ()

        # contact specified ranks and form the inter-comm
        requests = []
        for rank in ranks:
            requests += [ MPI.COMM_WORLD.isend (port, dest=rank) ]
        MPI.Request.waitall (requests)
        workers = self.accept (port, verbosity)

        # broadcast contract to all workers
        workers.bcast (contract, root=MPI.ROOT)

        # broadcast port, task template and the connector to workers
        workers.bcast ((port, task, self), root=MPI.ROOT)

        # disconnect from workers
        workers.Disconnect ()
        workers = None

        return port

    @staticmethod
    def shutdown (port, verbosity):
        """Finalize connector."""

        MPI.Close_port (port)

    @staticmethod
    def connect (port, peers):
        """Establish connection on worker side."""

        manager = peers.Connect (port)
        return manager

    @staticmethod
    def accept (port, verbosity):
        """Establish connection on manager side."""

        workers = MPI.COMM_SELF.Accept (port)
        return workers

    @staticmethod
    def disconnect (workers, verbosity):
        """Interrupt connection."""

        workers.Disconnect ()
