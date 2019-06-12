# # # # # # # # # # # # # # # # # # # # # # # # # #
# Convenience functions for connectors
#
# Jonas Šukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from mpi4py import MPI
import argparse

def universe_address ():
    """Return rank in MPI COMM_WORLD"""

    address = MPI.COMM_WORLD.Get_rank ()
    return address

def select (name = 'auto', verbosity = 0):
    """Automatically select the connector, or specify it manually by its name."""

    if name == 'auto':
        parser = argparse.ArgumentParser ()
        help = "connector to be used"
        choices = ['spawn', 'split', 'legacy']
        parser.add_argument ("--connector", type = str, help = help, choices = choices)
        args, unknown = parser.parse_known_args ()
        name = args.connector
        if name is None:
            if MPI.COMM_WORLD.Get_size () == 1:
                name = 'spawn'
            else:
                name = 'split'

    if universe_address () == 0:
        print (' :: CONNECTOR: %s' % name)

    if name == 'spawn':
        from spux.executors.mpi4py.connectors.spawn import Spawn
        connector = Spawn (verbosity)

    elif name == 'split':
        from spux.executors.mpi4py.connectors.split import Split
        connector = Split (verbosity)

    elif name == 'legacy':
        from spux.executors.mpi4py.connectors.legacy import Legacy
        connector = Legacy (verbosity)

    else:
        if universe_address () == 0:
            print (' :: WARNING: Connector "%s" not found, falling back to Spawn () connector.' % name)
        from spux.executors.mpi4py.connectors.spawn import Spawn
        connector = Spawn (verbosity)

    connector.barrier ()

    return connector