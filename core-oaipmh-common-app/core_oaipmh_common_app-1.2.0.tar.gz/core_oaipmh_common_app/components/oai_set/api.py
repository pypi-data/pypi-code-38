"""
OaiSet API
"""

from core_oaipmh_common_app.components.oai_set.models import OaiSet


def get_by_id(oai_set_id):
    """ Get an OaiSet by its id.

   Args:
       oai_set_id: OaiSet id.

   Returns: The OaiSet instance.

   """
    return OaiSet.get_by_id(oai_set_id)


def get_by_set_spec(set_spec):
    """ Get an OaiSet by its set_spec.

    Args:
        set_spec: OaiSet set_spec.

    Returns: The OaiSet instance.

    """
    return OaiSet.get_by_set_spec(set_spec=set_spec)


def get_all():
    """ Return all OaiSet

    Returns:
        List of OaiSet

    """
    return OaiSet.get_all()


def get_all_by_list_ids(list_oai_set_ids):
    """ Return all OaiSet by a list of ids.

    Returns:
        List of OaiSet

    """
    return OaiSet.get_all_by_list_ids(list_oai_set_ids)
