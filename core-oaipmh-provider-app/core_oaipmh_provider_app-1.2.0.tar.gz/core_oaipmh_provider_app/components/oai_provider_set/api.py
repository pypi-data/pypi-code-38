"""
OaiProviderSet API
"""
from core_oaipmh_provider_app.components.oai_provider_set.models import OaiProviderSet
from core_main_app.components.template_version_manager import api as template_version_manager_api



def upsert(oai_provider_set):
    """ Create or update an OaiProviderSet.

    Args:
        oai_provider_set:

    Returns:
        The OaiProviderSet instance.

    """
    return oai_provider_set.save()


def delete(oai_provider_set):
    """ Delete an OaiProviderSet.

    Args:
        oai_provider_set: The OaiProviderSet to delete.

    """
    oai_provider_set.delete()


def get_by_id(oai_provider_set_id):
    """ Get an OaiProviderSet by its id.

    Args:
        oai_provider_set_id: The OaiProviderSet id.

    Returns:
        The OaiProviderSet instance.

    """
    return OaiProviderSet.get_by_id(oai_set_id=oai_provider_set_id)


def get_by_set_spec(set_spec):
    """ Get an OaiProviderSet by its set_spec.

    Args:
        set_spec: The OaiProviderSet set_spec.

    Returns:
        The OaiProviderSet instance.
    """
    return OaiProviderSet.get_by_set_spec(set_spec=set_spec)


def get_all(order_by_field=None):
    """ Get all OaiProviderSet.
    Args:
        order_by_field: Order by field.

    Returns:
        List of OaiProviderSet.
    """
    return OaiProviderSet.get_all(order_by_field)


def get_all_by_templates_manager(templates_manager):
    """ Get all OaiProviderSet used by a list of templates manager.

    Args:
        templates_manager: List of templates manager.

    Returns:
        List of OaiProviderSet.

    """
    return OaiProviderSet.get_all_by_templates_manager(templates_manager=templates_manager)


def get_all_by_template_ids(template_ids):
    """ Get all OaiProviderSet used by a list of templates ids.

    Args:
        template_ids: List of templates ids.

    Returns:
        List of OaiProviderSet.

    """
    # Be sure to have string and not ObjectId()
    string_ids = map(str, template_ids)
    # Get all templates managers thanks to templates ids.
    templates_manager = template_version_manager_api.get_all_by_version_ids(string_ids)
    # Get all OaiProviderSet used by those templates manager
    return get_all_by_templates_manager(templates_manager)
