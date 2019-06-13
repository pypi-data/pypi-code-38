"""
*hynet* package configuration.

Parameters
----------
GENERAL : dict
    General settings.

    ``parallelize``: (``bool``)
        Enable or disable parallel processing in *hynet*. If True, certain
        procedures (e.g., the construction of constraint matrices for the OPF
        formulation) are parallelized if the system features more than one CPU.

OPF : dict
    Optimal power flow settings.

    ``pathological_price_profile_info``: (``bool``)
        Enable or disable the output of information about pathological price
        profiles under the hybrid architecture in the OPF summary. See also
        ``OPFResult`` and ``Scenario.has_hybrid_architecture``.

DISTRIBUTED : dict
    Settings for distributed computation.

    ``default_port``: (``int``)
        Default optimization server TCP port.
    ``default_authkey``: (``str``)
        Default optimization server authentication key.
    ``default_num_workers``: (``int``)
        Default number of worker processes on an optimization client.
    ``ssh_command``: (``str``)
        Command to run SSH on the local machine.
    ``python_command``: (``str``)
        Command to run Python on client machines.
"""

GENERAL = {
    'parallelize': True
}

OPF = {
    'pathological_price_profile_info': True
}

DISTRIBUTED = {
    'default_port': 1235,
    'default_authkey': 'hynet',
    'default_num_workers': 1,
    'ssh_command': 'ssh',
    'python_command': 'python'
}
