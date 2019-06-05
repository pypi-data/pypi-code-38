from ambition_sites import ambition_sites

from .constants import SINGLE_DOSE, CONTROL


class InvalidDrugAssignment(Exception):
    pass


def get_drug_assignment(row):
    """Returns drug_assignment as a word; 'single_dose' or 'control'.

    Converts a numeric drug_assignment or allocation
    to a word.
    """
    drug_assignment = row["drug_assignment"]
    if drug_assignment not in [SINGLE_DOSE, CONTROL]:
        if int(row["drug_assignment"]) == 2:
            drug_assignment = SINGLE_DOSE
        elif int(row["drug_assignment"]) == 1:
            drug_assignment = CONTROL
        else:
            raise InvalidDrugAssignment(
                f"Invalid drug assignment. "
                f'Got \'{row["drug_assignment"]}\'. Expected 1 or 2.'
            )
    return drug_assignment


def get_allocation(row, drug_assignment):
    """Returns an allocation as 1 or 2 for the given
    drug assignment or raises.
    """

    try:
        allocation = row["orig_allocation"]
    except KeyError:
        if drug_assignment == SINGLE_DOSE:
            allocation = "2"
        elif drug_assignment == CONTROL:
            allocation = "1"
        else:
            raise InvalidDrugAssignment(
                f"Invalid drug_assignment. Got {drug_assignment}."
            )
    return allocation


def get_site_name(long_name, row=None):
    """Returns the site name given the "long" site name.
    """
    try:
        site_name = [site for site in ambition_sites if site[2] == long_name][0][1]
    except IndexError as e:
        raise IndexError(f"{long_name} not found. Got {e}. See {row}")
    return site_name
