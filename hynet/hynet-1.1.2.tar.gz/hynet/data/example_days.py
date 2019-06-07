#pylint: disable=bad-whitespace
"""
Support for the generation of scenarios of exemplary days.
"""

import logging

import numpy as np

from hynet.data.interface import initialize_database, save_scenario

_log = logging.getLogger(__name__)

LOAD_WEIGHTS = {
    'winter_weekday':
        np.array([ 67,  63, 60, 59,  59,  60, 74,  86, 95, 96, 96,  95, 95,
                   95,  93, 94, 99, 100, 100, 96,  91, 83, 73, 63]) / 100,
    'winter_weekend':
        np.array([ 78,  72, 68, 66,  64,  65, 66,  70, 80, 88, 90,  91, 90,
                   88,  87, 87, 91, 100,  99, 97,  94, 92, 87, 81]) / 100,
    'summer_weekday':
        np.array([ 64,  60, 58, 56,  56,  58, 64,  76, 87, 95, 99, 100, 99,
                  100, 100, 97, 96,  96,  93, 92,  92, 93, 87, 72]) / 100,
    'summer_weekend':
        np.array([ 74,  70, 66, 65,  64,  62, 62,  66, 81, 86, 91,  93, 93,
                   92,  91, 91, 92,  94,  95, 95, 100, 93, 88, 80]) / 100
}


def initialize_database_with_example_days(database, base_case):
    """
    Initialize the database with the base case and add exemplary day scenarios.

    The added day scenarios are exemplary winter and summer weekdays/weekends
    obtained by scaling the base case load according to the data provided in
    [1]_, Table 4.

    Parameters
    ----------
    database : DBConnection
        Connection to the destination database. This database must be empty.
    base_case : Scenario
        Base case scenario for the new database.

    Raises
    ------
    ValueError
        In case that the destination database is not empty or the provided
        scenario data exhibits integrity or validity issues.

    References
    ----------
    .. [1]  C. Grigg et al., "The IEEE Reliability Test System - 1996. A report
            prepared by the Reliability Test System Task Force of the
            Application of Probability Methods Subcommittee," in IEEE Trans.
            Power Systems, vol. 14, no. 3, pp. 1010-1020, Aug. 1999.
    """
    base_case.verify()
    if not database.empty:
        raise ValueError("The destination database is not empty.")
    initialize_database(database, base_case)
    add_example_days(database, base_case)


def add_example_days(database, base_case):
    """Add the exemplary day scenarios to the database."""
    for scenario_name, weights in LOAD_WEIGHTS.items():
        scenario_name = scenario_name.replace('_', ' ').title()
        for time, weight in enumerate(weights):
            scenario_new = base_case.copy()
            scenario_new.name = scenario_name
            scenario_new.time = time
            scenario_new.bus['load'] *= weight
            save_scenario(database, scenario_new)
