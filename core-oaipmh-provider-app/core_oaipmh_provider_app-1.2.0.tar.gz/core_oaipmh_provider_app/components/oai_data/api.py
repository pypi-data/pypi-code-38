""" OaiData API
"""
from core_oaipmh_provider_app.components.oai_data.models import OaiData
from core_oaipmh_provider_app.commons import status
from core_main_app.commons import exceptions
from datetime import datetime


def upsert(oai_data):
    """ Create or update an OaiData.

    Args:
        oai_data: OaiData to create or update.

    Returns:
        OaiData instance.


    """
    return oai_data.save()


def delete(oai_data):
    """ Delete an OaiData.

    Args:
        oai_data: OaiData to delete.

    """
    oai_data.delete()


def get_by_id(oai_data_id):
    """ Get an OaiData by its id.

    Args:
        oai_data_id: Id of the OaiData.

    Returns:
        OaiData instance.

    """
    return OaiData.get_by_id(oai_data_id=oai_data_id)


def get_by_data(data):
    """ Get an OaiData by its data.

    Args:
        data: Data instance.

    Returns:
        OaiData instance.

    """
    return OaiData.get_by_data(data=data)


def get_all_by_template(template, from_date=None, until_date=None):
    """ Get all OaiData used by a template.

    Args:
        template: The template.
        from_date: From date
        until_date: Until date

    Returns:
        List of OaiData.

    """
    return OaiData.get_all_by_template(template=template, from_date=from_date, until_date=until_date)


def get_all():
    """ Get all OaiData.

    Returns:
        List of OaiData.

    """
    return OaiData.get_all()


def get_all_by_status(status_):
    """ Get all OaiData by their status.

    Args:
        status_: Status.

    Returns:
        List of OaiData.

    """
    return OaiData.get_all_by_status(status=status_)


def get_earliest_data_date():
    """ Get the earliest OaiData date
    Returns:
        Date of the earliest OaiData.

    """
    return OaiData.get_earliest_data_date()


def upsert_from_data(document, force_update=False):
    """ Create or Update an OaiData from a Data document.
    Args:
        document: Data document
        force_update: Force the Update of the OaiData (oai_date_stamp).

    Returns:

    """
    try:
        oai_data = get_by_data(document)
        if force_update:
            oai_data.oai_date_stamp = datetime.now()
            upsert(oai_data)
    except exceptions.DoesNotExist:
        # Create only if the record is published.
        oai_data = OaiData()
        oai_data.status = status.ACTIVE
        oai_data.data = document
        oai_data.template = document.template
        oai_data.oai_date_stamp = datetime.now()
        upsert(oai_data)
    except Exception:
        pass
