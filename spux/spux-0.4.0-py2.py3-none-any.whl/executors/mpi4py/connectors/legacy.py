# # # # # # # # # # # # # # # # # # # # # # # # # #
# Connector class for subdivision of MPI.COMM_WORLD into manager and workers
# using mpi4py bindings and MPI backend for distributed memory paralellization
# Legacy version of the 'Split' connector, avoiding the use of Accept/Connect
#
# Marco Bacci
# Eawag, Switzerland
# marco.bacci@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from mpi4py import MPI
from .utils import universe_address
from .split import Split, get_ranks

class Legacy (Split):
    """Class to establish workers MPI processes when dealing with legacy MPI implementations."""

    # connect manager with the number of requested workers by returning a port needed to connect to an inter-communicator
    def bootup (self, contract, task, resource, root, verbosity):
        """Inter-connect manager with the number of requested workers by returning leader rank."""

        # get ranks according to specified resources
        ranks = get_ranks (resource, root, manager=1)

        # get universe rank of manager, i.e., remote leader for workers
        manager_rank = universe_address ()

        # the remote leader of the workers is the one with local rank 0,
        # i.e., the one with the lowest universe rank
        remote_leader = min (ranks)

        # contact specified ranks and form the inter-comm
        requests = []
        for rank in ranks:
            requests += [ MPI.COMM_WORLD.isend (manager_rank, dest=rank) ]
        MPI.Request.waitall (requests)
        workers = self.accept (remote_leader, verbosity)

        # broadcast contract to all workers
        workers.bcast (contract, root=MPI.ROOT)

        # broadcast rank of leader, task template and the connector to workers
        workers.bcast ((manager_rank, task, self), root=MPI.ROOT)

        # disconnect from workers
        workers.Disconnect ()
        workers = None

        return remote_leader

    @staticmethod
    def shutdown (port, verbosity):
        """Finalize connector."""

        pass

    @staticmethod
    def connect (remote_leader, peers):
        """Establish connection on worker side."""

        manager = peers.Create_intercomm (local_leader=0, peer_comm=MPI.COMM_WORLD, remote_leader=remote_leader, tag=remote_leader)
        return manager

    @staticmethod
    def accept (remote_leader, verbosity):
        """Establish connection on manager side."""

        manager_rank = universe_address ()
        workers = MPI.COMM_SELF.Create_intercomm (local_leader=0, peer_comm=MPI.COMM_WORLD, remote_leader=remote_leader, tag=manager_rank)
        return workers

    @staticmethod
    def disconnect (workers, verbosity):
        """Interrupt connection."""

        workers.Disconnect ()
