# # # # # # # # # # # # # # # # # # # # # # # # # #
# Worker for the Spawn connnector class
# using mpi4py bindings and MPI backend for distributed memory paralellization
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from mpi4py import MPI
import sys

def universe_address ():
    """Return rank in MPI COMM_WORLD"""

    address = MPI.COMM_WORLD.Get_rank ()
    return address

# get 'manager' inter-communicator
manager = MPI.Comm.Get_parent ()

# get 'peers' intra-communicator
peers = MPI.COMM_WORLD

# set python path
sys.path.insert (0, '.')

# get contract and work according to it
contract = manager.bcast (None)
contract (manager, peers)
