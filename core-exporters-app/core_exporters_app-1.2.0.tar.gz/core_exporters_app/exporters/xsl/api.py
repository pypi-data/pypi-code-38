""" Exporter XSL api
"""
from core_exporters_app.exporters.xsl.models import ExporterXsl
from core_exporters_app.commons.constants import XSL_URL
import core_main_app.components.xsl_transformation.api as xsl_transformation_api


def get_all(is_cls=True):
    """ Returns all XSL exporters

    Returns:
        XSL exporter collection

    """
    return ExporterXsl.get_all(is_cls)


def get_all_xsl_id():
    """ Returns all xsl transformation id

    Returns:
        XSL exporter collection

    """
    return [str(exporter.xsl_transformation.id) for exporter in get_all()]


def get_all_by_xsl_id_list(xsl_id_list):
    """ Returns all Xsl exporter with the given id list

    Returns:
        XSL exporter collection

    """
    return ExporterXsl.get_all_by_xsl_id_list(xsl_id_list)


def upsert(exporter):
    """ upsert the exporter

    Args:
        exporter:

    Returns:

    """
    return exporter.save()


def upsert_or_delete_exporter_xsl(xsl_list):
    """ Upsert or delete exporter xslt

        If Exist in database and not in list -> Delete If does not contains associated templates
        If Exist in list and not in database -> Upsert

    Args:
        xsl_list: xsl id list

    Returns:

    """
    # get all xslt id already registered as exporter
    xsl_list_from_database = get_all_xsl_id()

    # get all xsl id for deletion
    xsl_id_list_for_deletion = set(xsl_list_from_database).difference(xsl_list)

    # get all exporter with the xsl id list given
    exporter_list_for_deletion = []
    if len(xsl_id_list_for_deletion) > 0:
        exporter_list_for_deletion = get_all_by_xsl_id_list(xsl_id_list_for_deletion)

    # deletes all exporter not in list but in database without associated templates
    for exporter in exporter_list_for_deletion:
        exporter.delete()

    # get all xsl id to upsert as Exporter
    list_for_upsert = set(xsl_list).difference(xsl_list_from_database)

    # upsert all exporter is in list but not in database
    for xsl_id in list_for_upsert:
        xsl_transformation = xsl_transformation_api.get_by_id(xsl_id)
        exporter = ExporterXsl(name=xsl_transformation.name,
                               url=XSL_URL,
                               enable_by_default=False,
                               xsl_transformation=xsl_transformation)
        upsert(exporter)
