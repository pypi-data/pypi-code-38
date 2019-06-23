def loadPrivateTuples():
    """ Load Private Tuples

    In this method, we load the private tuples.
    This registers them so the Vortex can reconstructed them from
    serialised data.

    """
    from . import GisDiagramTuple
    GisDiagramTuple.__unused = False

    from . import AddIntValueActionTuple
    AddIntValueActionTuple.__unused = False

    from . import StringCapToggleActionTuple
    StringCapToggleActionTuple.__unused = False
