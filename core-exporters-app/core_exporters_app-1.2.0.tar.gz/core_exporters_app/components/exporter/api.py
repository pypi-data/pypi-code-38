""" Exporter api
"""
from core_exporters_app.components.exporter.models import Exporter


def get_all(is_cls=True):
    """ Lists all exporters

    Returns: exporter collection

    """
    return Exporter.get_all(is_cls)


def get_all_default_exporter():
    """ Lists all default exporters

    Returns: exporter collection

    """
    return Exporter.get_all_default_exporter()


def get_all_by_url(url):
    """ Lists all exporters with the given url

    Args:
        url:

    Returns:

    """
    return Exporter.get_all_by_url(url)


def get_by_id(exporter_id):
    """ Returns exporter object with the given id

    Args:
        exporter_id:

    Returns: exporter object

    """
    return Exporter.get_by_id(exporter_id)


def get_by_url(exporter_url):
    """ Returns exporter object with the given url

    Args:
        exporter_url:

    Returns: exporter object

    """
    return Exporter.get_by_url(exporter_url)


def get_all_by_template_list(template_id_list):
    """ Returns all exporters object available for id templates given

    Args:
        template_id_list:

    Returns:

    """
    return Exporter.get_all_by_template_list(template_id_list)


def upsert(exporter):
    """Saves or updates exporter

    Args:
        exporter:

    Returns:

    """
    return exporter.save_object()
