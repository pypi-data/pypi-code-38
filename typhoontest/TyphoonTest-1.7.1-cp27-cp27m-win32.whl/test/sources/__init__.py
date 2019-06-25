""" This package contains high-level functions for dealing with power sources. """
from . import impl as _impl


def get_phasor_3ph(gridsimname, alias=None):
    """ Reads a Phasor3ph out of the chosen GridSimulator.

    Parameters
    ----------
    gridsimname
        Name of the grid. Should be a grid simulator in the HIL.
    alias
        Custom name for the returned phasors.

    Returns
    -------
    Phasors3ph
        Grid phasors


    Examples
    --------
    Considering an already running simulation:

    >>> from typhoon.test.sources import get_phasor_3ph
    >>> phasors = get_phasor_3ph("Grid Simulator1", alias="Initial Grid")
    >>> print(phasors)

    Notes
    -----

    Check the Phasors3ph page to see more possibilities when using phasors.

    See Also
    --------
    typhoon.types.phasors.Phasors3ph
    """
    return _impl.get_phasor_3ph(gridsimname, alias)


def change_grid(gridname, rms=None, frequency=None, phase=None, alias=None):
    """ Change grid characteristics.

    Parameters
    ----------
    gridname
        Name of the grid. Should be a grid simulator in the HIL.
    rms : number or 3-element sequence
        RMS values. If a single number, applies the same for each phase.
    frequency : number
        Frequency in Hertz. Applies the same for each phase.
    phase : number or 3-element sequence (list or tuple)
        Phase in degrees. If a single number, applies the same for each phase.
    alias
        Custom name for this grid change. This name is considered in the aliases of returned values.

    Returns
    -------
    namedtuple
        With the following attributes:
    t : Timedelta
        Time of the grid fault.
    phasors_before : Phasors3ph
        Grid phasors before the fault
    phasors_after : Phasors3ph
        Grid phasors after the fault


    Examples
    --------
    >>> from typhoon.test.sources import change_grid
    >>> voltage = 220
    >>> fault_level = 1.05
    >>> fault = change_grid("Grid Simulator1", rms=fault_level*voltage, alias="Fault")
    >>> print(fault.t)
    >>> print(fault.phasors_before)
    >>> print(fault.phasors_after)
    """
    return _impl.change_grid(gridname, rms, frequency, phase, alias)


def get_pv_mpp(panel, alias=None):
    """ Get maximum power point information from a PV panel.

    This is an improved version of the HIL API ``get_pv_mpp`` function, also returning power.

    Parameters
    ----------
    panel
        Name of the PV Panel.
    alias
        Custom name for this MPP conditions.

    Returns
    -------
    namedtuple
        With the following attributes:
    v : float
        MPP Voltage
    i : float
        MPP Current
    p : float
        MPP Power


    Examples
    --------
    >>> from typhoon.test.sources import get_pv_mpp
    >>> mpp = get_pv_mpp("PV Panel 1")
    >>> print(mpp.v)
    >>> print(mpp.i)
    >>> print(mpp.p)
    """
    return _impl.get_pv_mpp(panel, alias)
