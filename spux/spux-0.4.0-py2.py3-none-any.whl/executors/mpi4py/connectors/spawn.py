# # # # # # # # # # # # # # # # # # # # # # # # # #
# Connector class for spawning workers directly from the manager at the OS level
# using mpi4py bindings and MPI backend for distributed memory paralellization
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from mpi4py import MPI
import os
import sys

class Spawn (object):
    """Class to establish workers MPI processes by spawning of new processes."""

    def __init__ (self, verbosity = 0):

        self.verbosity = verbosity

    # connect manager with the number of requested workers by returning a port needed to connect to an inter-communicator
    def bootup (self, contract, task, resource, root=0, verbosity=0):
        """Return means of inter-communication along a possible hierarchy of processes."""

        directory, filename = os.path.split (os.path.realpath (__file__))
        worker = os.path.join (directory, "worker.py")
        info = MPI.Info.Create ()
        info.Set ('wdir', os.getcwd ())
        if verbosity:
           print ("Spawning workers:", resource ['workers'])
        workers = MPI.COMM_SELF.Spawn (sys.executable, args=[worker], maxprocs=resource ['workers'], info=info)
        # n = MPI.COMM_SELF.Get_attr (MPI.UNIVERSE_SIZE)

        # broadcast contract to workers
        workers.bcast (contract, root=MPI.ROOT)

        # open a port for workers to connect to
        port = MPI.Open_port ()

        # broadcast port, task template and the connector to workers
        workers.bcast ((port, task, self), root=MPI.ROOT)

        # disconnect from workers
        workers.Disconnect ()
        workers = None

        return port

    def barrier (self):

        return None

    def init (self, resources):

        return None

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
        """Establish connection."""

        workers = MPI.COMM_SELF.Accept (port)
        return workers

    @staticmethod
    def disconnect (workers, verbosity):
        """Interrupt connection."""

        workers.Disconnect ()
