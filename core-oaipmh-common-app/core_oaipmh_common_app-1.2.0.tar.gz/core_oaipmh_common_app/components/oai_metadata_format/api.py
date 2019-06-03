"""
OaiMetadataFormat API
"""

from core_oaipmh_common_app.components.oai_metadata_format.models import OaiMetadataFormat
from core_main_app.commons import exceptions


def get_by_id(oai_metadata_format_id):
    """ Get an OaiMetadataFormat by its id.

    Args:
        oai_metadata_format_id: OaiMetadataFormat id.

    Returns: The OaiMetadataFormat instance.

    """
    return OaiMetadataFormat.get_by_id(oai_metadata_format_id)


def get_by_metadata_prefix(metadata_prefix):
    """ Get an OaiMetadataFormat by its metadata prefix.

    Args:
        metadata_prefix: OaiMetadataFormat metadata prefix.

    Returns: The OaiMetadataFormat instance.

    """
    return OaiMetadataFormat.get_by_metadata_prefix(metadata_prefix=metadata_prefix)


def get_all():
    """
    Get all OaiMetadataFormat
    :return:
    """
    return OaiMetadataFormat.get_all()


def get_all_by_list_ids(list_oai_metadata_format_ids):
    """
    Get all OaiMetadataFormat by a list of ids
    :param list_oai_metadata_format_ids:
    :return:
    """
    return OaiMetadataFormat.get_all_by_list_ids(list_oai_metadata_format_ids)
